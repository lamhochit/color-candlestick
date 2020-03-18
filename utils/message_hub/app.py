import os
from requests import post, get

try:
    from upload_file import upload_file
except:
    from .upload_file import upload_file

prod_ser = 'https://api.invbots.com/message-hub'
dev_ser = 'https://api.invbots.dev/message-hub'
local_ser = 'http://localhost:8964/message-hub'


# digitalocean-python-manager
# https://github.com/Mashoud123/digitalocean-python-manager/blob/master/app.py

class MessageHub:
    """
        run help()
    """

    def __init__(self, env='dev'):
        self.messages = []
        if env == 'prod':
            self.API = prod_ser
        elif env == 'dev':
            self.API = dev_ser
        elif env == 'local':
            self.API = local_ser

    def __del__(self):
        print('MessageHub is exiting')

    class Message:
        def __init__(self, channel: str, recipient: [str], message: {str}, file=None):
            self.channel = channel
            self.recipient = recipient
            self.message = message
            self.file = file

    def add_message(self, channel: str, recipient: [str], message: {str}, file=None):
        try:
            if file is None:
                message = self.Message(channel, recipient, message)
            else:
                message = self.Message(channel, recipient, message, upload_file(file))
        except Exception as e:
            print("Exception in add_message:\n", e)
            raise e
        finally:
            self.messages.append(message)

    def post_all(self):
        for message in self.messages:
            the_json = {'channel': message.channel, 'recipient': message.recipient, "message": message.message,
                        "file": message.file}
            post_res = post(f'{self.API}', json=the_json)
            print('--post_message--\n', post_res.json())

    def help(self):
        print(get(f'{self.API}/help').text)


if __name__ == '__main__':
    MessageHubHelper = MessageHub()
    # MessageHubHelper.add_message('email', ['frankchaninvbots@gmail.com', 'frank.chan@invbots.com'],
    # {'subject': '222sub', 'text': '222con'})
    # MessageHubHelper.add_message('email', 'frank.chan@invbots.com',
    #                              {'subject': 'app.py', 'text': 'app.22py'},
    #                              {'filePath': 'app.py', 'sendAs': 'attachment'})
    MessageHubHelper.add_message('slack', ['testing_slack', 'UACNX5CA1'], {'text': 'xxxxxxxxxxxxxxxx'},
                                 {'filePath': 'app.py', 'sendAs': 'attachment'})
    # MessageHubHelper.add_message('slack', ['testing_slack', 'random'], {'text': 'aa'},
    #                              {'filePath': 'readme.md', 'sendAs': 'attachment'})
    # MessageHubHelper.add_message('slack', 'testing_slack', {'text': 'f123121'})
    # MessageHubHelper.add_message('facebook', 'hotung.chan.58', {'text': 'f123121'})
    # MessageHubHelper.add_message('telegram', '243680660', {'text': 'f12telegramtelegram3121'})
    MessageHubHelper.post_all()
    # MessageHubHelper.help()
