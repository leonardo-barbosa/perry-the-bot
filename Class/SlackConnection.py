# -*- coding: UTF-8 -*-
from slackclient import SlackClient
import os

class SlackConnection:
    def __init__(self):
        self._token = os.environ.get('SLACK_TOKEN', None)
        self._sc = SlackClient(self._token)

    def send_message(self, ticket):

        dic = [
                {
                    "fallback": "Novo ticket",
                    "pretext": "<!here> New ticket on queue",
                    "title": "Ticket #{0} : {1}".format(ticket.id, ticket.subject),
                    "title_link": "https://pagarme.zendesk.com/agent/tickets/{0}".format(ticket.id),
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
        except Exception as e:
            print(e.args)

    def notify_supporter(self, slack_id, name, ticket):
        ticket_url = "https://pagarme.zendesk.com/agent/tickets/{0}".format(ticket.id)
        message = "Agente {0}, tem ticket novo pra você! \n {1}".format(name, ticket_url)
        self.message_channel(slack_id, message)

    def notify_pending_interaction_ticket(self, slack_id, name, ticket, interval):
        ticket_url = "https://pagarme.zendesk.com/agent/tickets/{0}".format(ticket.id)
        message = "Agente {0}, o ticket {1} ultrapassou {2} horas sem interação!".format(mongoSup["name"], ticket_url, interval)
        self.message_channel(slack_id, message)

    def message_channel(self, channel_id, message):
        try:
            print(
                self._sc.api_call(
                "chat.postMessage",
                channel=channel_id,
                text=message
            ))
        except Exception as e:
            print(e.args)
