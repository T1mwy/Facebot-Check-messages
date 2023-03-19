import requests
import time
import json
from datetime import datetime

access_token = 'Access_Token'
group_id = 'Group_ID'
# Set the name of the log file
log_file = 'Data/Messages_Deleted.json'
# Set the name of the user data file
user_file = 'Data/Users.json'
with open('Data/keywords.json') as f:
    keywords = json.load(f)

while True:
    response = requests.get(
        f'https://graph.facebook.com/v12.0/{group_id}/feed',
        params={'access_token': access_token}
    )

    if response.ok:
        messages = response.json()['data']
        deleted_messages = []
        for message in messages:
            for keyword in keywords:
                if keyword in message['message']:
                    response = requests.delete(
                        f'https://graph.facebook.com/v12.0/{message["id"]}',
                        params={'access_token': access_token}
                    )
                    if response.ok:
                        user_response = requests.get(
                            f'https://graph.facebook.com/v12.0/{message["from"]["id"]}',
                            params={'access_token': access_token, 'fields': 'name'}
                        )
                        if user_response.ok:
                            user_data = user_response.json()
                            user = {'id': message['from']['id'], 'name': user_data.get('name', '')}
                            # Append the user data to the existing file
                            with open(user_file, 'a') as f:
                                # Write the user data as formatted JSON
                                json.dump(user, f, indent=4, sort_keys=True)
                                # Write a newline character after the JSON object
                                f.write('\n')
                            print(f'User "{user["name"]}" ({user["id"]}) deleted message "{message["message"]}"')
                        else:
                            print(f'Failed to get user data for user "{message["from"]["id"]}".')
                        deleted_messages.append({
                            'message': message['message'],
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'user_id': message['from']['id']
                        })
                        print(f'Message "{message["message"]}" deleted successfully!')
                    else:
                        print(f'Failed to delete message "{message["message"]}".')
        if deleted_messages:
            # Append the log to the existing file
            with open(log_file, 'a') as f:
                # Write the logs as formatted JSON
                json.dump(deleted_messages, f, indent=4, sort_keys=True)
                # Write a newline character after the JSON object
                f.write('\n')
            print(f'{len(deleted_messages)} messages deleted. Log saved to {log_file}.')

            # Print the logs in the console
            for message in deleted_messages:
                print(f'{message["timestamp"]} - User "{message["user_id"]}" deleted message "{message["message"]}"')
        else:
            print('No messages deleted.')
    else:
        print('Failed to retrieve messages.')

    # Wait for 1 minute before checking again
    time.sleep(60)