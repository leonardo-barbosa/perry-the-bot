import xml.etree.ElementTree as Et
from Class import SlackConnection
from zenpy import Zenpy

import utilities
from Dicty import agents


class ZendeskConnection:
    def __init__(self):
        self._configs = Et.parse('config.xml')
        self._credentials = self._configs.find('config')
        self._creds = {
            'email': self._credentials.find('username').text,
            'password': self._credentials.find('password').text,
            'subdomain': self._credentials.find('subdomain').text
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

    def assign_tickets(self):
        sups = self._get_supporters()
        name = ''

        # open queue_marker.txt file
        file = utilities.open_file()
        marker = int(file.read())

        for ticket in self._get_not_assigned_tickets():
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
                self._sl.send_message(slack_id, name, ticket)
                utilities.clear_n_write_file(file, marker)
            except Exception as e:
                print(e.args)
