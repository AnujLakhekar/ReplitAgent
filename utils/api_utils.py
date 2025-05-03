import requests
import json
import logging
import os
import time
from urllib.parse import urlparse, urljoin
import hashlib

def fetch_data(url, method='GET', headers=None, params=None, data=None, timeout=30):
    """
    Fetch data from an API endpoint.
    
    Args:
        url (str): URL to fetch data from
        method (str): HTTP method to use (GET, POST, PUT, DELETE)
        headers (dict): HTTP headers
        params (dict): Query parameters
        data (dict): Request body data
        timeout (int): Request timeout in seconds
    
    Returns:
        dict: Response data
    """
    if headers is None:
        headers = {}
    
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=data if data else None,
            timeout=timeout
        )
        
        # Raise an exception for HTTP errors
        response.raise_for_status()
        
        # Try to parse as JSON, fallback to text if not JSON
        try:
            return response.json()
        except ValueError:
            return {"text": response.text}
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {url}: {str(e)}")
        raise

def download_file(url, destination, headers=None, timeout=60):
    """
    Download a file from a URL.
    
    Args:
        url (str): URL to download from
        destination (str): Local path to save the file
        headers (dict): HTTP headers
        timeout (int): Request timeout in seconds
    
    Returns:
        str: Path to the downloaded file
    """
    if headers is None:
        headers = {}
    
    try:
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(destination)), exist_ok=True)
        
        # Stream the download to allow for large files
        with requests.get(url, headers=headers, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            with open(destination, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        return destination
    except Exception as e:
        logging.error(f"Error downloading file from {url}: {str(e)}")
        raise

def post_data(url, data, headers=None, timeout=30):
    """
    Post data to an API endpoint.
    
    Args:
        url (str): URL to post data to
        data (dict): Data to post
        headers (dict): HTTP headers
        timeout (int): Request timeout in seconds
    
    Returns:
        dict: Response data
    """
    return fetch_data(url, method='POST', headers=headers, data=data, timeout=timeout)

def put_data(url, data, headers=None, timeout=30):
    """
    Put data to an API endpoint.
    
    Args:
        url (str): URL to put data to
        data (dict): Data to put
        headers (dict): HTTP headers
        timeout (int): Request timeout in seconds
    
    Returns:
        dict: Response data
    """
    return fetch_data(url, method='PUT', headers=headers, data=data, timeout=timeout)

def delete_data(url, headers=None, timeout=30):
    """
    Delete data from an API endpoint.
    
    Args:
        url (str): URL to delete data from
        headers (dict): HTTP headers
        timeout (int): Request timeout in seconds
    
    Returns:
        dict: Response data
    """
    return fetch_data(url, method='DELETE', headers=headers, timeout=timeout)

def handle_rate_limiting(response, retry_after=None, max_retries=3):
    """
    Handle rate-limiting in API responses.
    
    Args:
        response (requests.Response): Response object
        retry_after (int): Seconds to wait before retrying, or None to use response headers
        max_retries (int): Maximum number of retries
    
    Returns:
        requests.Response: Response after successful retry or the original response
    """
    retries = 0
    
    while response.status_code == 429 and retries < max_retries:
        retries += 1
        
        # Determine how long to wait
        if retry_after is None:
            retry_after_header = response.headers.get('Retry-After')
            if retry_after_header:
                try:
                    wait_time = int(retry_after_header)
                except ValueError:
                    # If it's a date, we need to parse it
                    wait_time = 10  # Default to 10 seconds if we can't parse
            else:
                wait_time = 2 ** retries  # Exponential backoff
        else:
            wait_time = retry_after
        
        logging.info(f"Rate limited. Retrying after {wait_time} seconds (retry {retries}/{max_retries})")
        time.sleep(wait_time)
        
        # Retry the request
        response = requests.request(
            method=response.request.method,
            url=response.request.url,
            headers=response.request.headers,
            data=response.request.body
        )
    
    return response

def create_webhook(url, callback_url, events=None, headers=None):
    """
    Create a webhook subscription.
    
    Args:
        url (str): API endpoint to create the webhook
        callback_url (str): URL to receive webhook events
        events (list): List of events to subscribe to
        headers (dict): HTTP headers
    
    Returns:
        dict: Webhook subscription details
    """
    if headers is None:
        headers = {}
    
    if events is None:
        events = ["*"]  # Subscribe to all events by default
    
    data = {
        "url": callback_url,
        "events": events
    }
    
    try:
        return post_data(url, data, headers)
    except Exception as e:
        logging.error(f"Error creating webhook: {str(e)}")
        raise

def verify_webhook(request_data, secret, signature_header):
    """
    Verify a webhook signature.
    
    Args:
        request_data (bytes): Raw request body data
        secret (str): Webhook secret
        signature_header (str): Signature from the request headers
    
    Returns:
        bool: True if the signature is valid
    """
    try:
        if not signature_header:
            return False
        
        # Calculate the HMAC signature
        computed_signature = "sha256=" + hmac.new(
            secret.encode('utf-8'),
            request_data,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        return hmac.compare_digest(computed_signature, signature_header)
    except Exception as e:
        logging.error(f"Error verifying webhook signature: {str(e)}")
        return False

def paginate_requests(url, headers=None, params=None, max_pages=None):
    """
    Paginate through API results.
    
    Args:
        url (str): Base URL for the API
        headers (dict): HTTP headers
        params (dict): Initial query parameters
        max_pages (int): Maximum number of pages to fetch, or None for all
    
    Returns:
        list: Combined results from all pages
    """
    if headers is None:
        headers = {}
    
    if params is None:
        params = {}
    
    all_results = []
    page = 1
    more_pages = True
    
    while more_pages and (max_pages is None or page <= max_pages):
        # Update page parameter
        current_params = params.copy()
        current_params['page'] = page
        
        try:
            response = fetch_data(url, headers=headers, params=current_params)
            
            # Different APIs handle pagination differently
            # This is a common pattern, but may need to be adjusted
            if isinstance(response, dict):
                results = response.get('results', [])
                all_results.extend(results)
                
                # Check if there are more pages
                more_pages = response.get('next') is not None
            elif isinstance(response, list):
                all_results.extend(response)
                
                # If the response is empty or smaller than expected, assume no more pages
                more_pages = len(response) > 0
            else:
                more_pages = False
            
            page += 1
        except Exception as e:
            logging.error(f"Error during pagination at page {page}: {str(e)}")
            raise
    
    return all_results

def build_url(base_url, path=None, params=None):
    """
    Build a URL with path and query parameters.
    
    Args:
        base_url (str): Base URL
        path (str): Path to append to the base URL
        params (dict): Query parameters
    
    Returns:
        str: Complete URL
    """
    url = base_url
    
    if path:
        url = urljoin(url, path)
    
    if params:
        # Filter out None values
        filtered_params = {k: v for k, v in params.items() if v is not None}
        
        # Add query parameters if any remain after filtering
        if filtered_params:
            from urllib.parse import urlencode
            url = f"{url}?{urlencode(filtered_params)}"
    
    return url
