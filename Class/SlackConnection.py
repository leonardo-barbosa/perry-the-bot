from slackclient import SlackClient
import os


class SlackConnection:
    def __init__(self):
        self._token = os.environ.get('SLACK_TOKEN', None)
        self._sc = SlackClient(self._token)

    def send_message(self, slack_id, name, ticket):

        dic = [
                {
                    "fallback": "Novo ticket",
                    "pretext": "<!here> New ticket on queue",
                    "title": "Ticket #{0} : {1}".format(ticket.id, ticket.subject),
                    "title_link": ticket.url,
                    "text": "{0}".format(ticket.description),
                    "color": "#7CD197",
                    "callback_id": "{0}".format(ticket.id),
                    "actions": [
                        {
                            "name": "btnDuvida",
                            "text": "Duvida",
                            "style": "primary",
                            "type": "button",
                            "value": "1"
                        },
                        {
                            "name": "btnProblema",
                            "text": "Problema",
                            "style": "primary",
                            "type": "button",
                            "value": "2"
                        },
                        {
                            "name": "btnTarefa",
                            "text": "Tarefa",
                            "style": "primary",
                            "type": "button",
                            "value": "3"
                        },
                        {
                            "name": "btnAtendimento",
                            "text": "Enviar para atendimento",
                            "style": "primary",
                            "type": "button",
                            "value": "4"
                        }
                    ]
                }
        ]

        try:
            print(self._sc.api_call(
                "chat.postMessage",
                channel="#realsuporte",
                attachments=dic
            ))
            self._notify_supporter(slack_id, name, ticket)
        except Exception as e:
            print(e.args)

    def _notify_supporter(self, slack_id, name, ticket):

        try:
            print(self._sc.api_call(
                "chat.postMessage",
                channel=slack_id,
                text="Agente {0}, tem ticket novo pra você! \n {1}".format(name, ticket.url)
            ))
        except Exception as e:
            print(e.args)
