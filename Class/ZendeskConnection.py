from zenpy import Zenpy
from Class import SlackConnection

import utilities
from Dicty import agents
import os


class ZendeskConnection:
    def __init__(self):
        self._creds = {
            'email': os.environ.get('ZENDESK_USER', None),
            'password': os.environ.get('ZENDESK_PASS', None),
            'subdomain': "pagarme"
        }
        self._zenpy_client = Zenpy(**self._creds)
        self._sl = SlackConnection.SlackConnection()

    def _get_supporters(self):
        supporter_list = []

        for supporter in self._zenpy_client.search(type='user', group_id=21164867):
            for email in agents.ASSIGN:
                if supporter.email in email['email']:
                    try:
                        supporter_list.append(supporter)
                    except Exception as e:
                        print(e.args)
        return supporter_list

    def _get_not_assigned_tickets(self):
        not_assigned_tickets = list()

        for tickets in self._zenpy_client.search(type='ticket', group_id=21164867,
                                                 assignee_id=None, status=['new', 'open', 'pending']):
            not_assigned_tickets.append(tickets)

        return not_assigned_tickets

    def _typing_tickets(self):
        not_assigned_tickets_with_type = list()
        fl = open("../ticket_log.txt", "r+")
        read_file_string = fl.read()
        for ticket in self._get_not_assigned_tickets():
            if ticket.type in ['problem', 'incident', 'question', 'task']:
                not_assigned_tickets_with_type.append(ticket)
            else:
                if str(ticket.id) not in read_file_string:
                    self._sl.send_message(ticket)
                    fl.write("  " + ticket.id)

        return not_assigned_tickets_with_type

    def assign_tickets(self):
        sups = self._get_supporters()
        name = ''

        # open queue_marker.txt file
        fl = utilities.open_file()
        marker = int(fl.read())

        for ticket in self._typing_tickets():
            if marker >= len(sups):
                marker = 0
            try:
                ticket.assignee = sups[marker]
                for sup in agents.ASSIGN:
                    if sup['email'] == sups[marker].email:
                        slack_id = sup['slack_id']
                        name = sup['name']
                print(slack_id + " | " + sups[marker].name)
                marker += 1
                self._zenpy_client.tickets.update(ticket)
                self._sl.notify_supporter(slack_id, name, ticket)
                utilities.clear_n_write_file(fl, marker)
            except Exception as e:
                print(e.args)
