import requests

from logger.log_main import get_logger


def fetchUserGroups(userToken, nextLink=None):
    logger = get_logger()
    
    # Recursively fetch group membership
    if nextLink:
        endpoint = nextLink
    else:
        endpoint = "https://graph.microsoft.com/v1.0/me/transitiveMemberOf?$select=id"
    
    headers = {
        'Authorization': "bearer " + userToken
    }
    try :
        response = requests.get(endpoint, headers=headers)
        if response.status_code != 200:
            logger.error(f"Error fetching user groups: {response.status_code} {response.text}")
            return []
        
        response = response.json()
        if "@odata.nextLink" in response:
            nextLinkData = fetchUserGroups(userToken, response["@odata.nextLink"])
            response['value'].extend(nextLinkData)
        
        return response['value']
    except Exception as e:
        logger.error(f"Exception in fetchUserGroups: {e}")
        return []