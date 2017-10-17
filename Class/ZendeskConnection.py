from zenpy import Zenpy
from Class import SlackConnection
from Class import MongoConnection

import utilities
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
        self._mc = MongoConnection.MongoConnection()

    def _get_supporters(self):
        supporter_list = []

        for supporter in self._zenpy_client.search(type='user', group_id=21164867):
            for email in self._mc.get_active_supporters():
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
        fl = open("ticket_log.txt", "r+")
        read_file_string = fl.read()

        for ticket in self._get_not_assigned_tickets():
            if ticket.type in ['problem', 'incident', 'question', 'task']:
                not_assigned_tickets_with_type.append(ticket)
            else:
                if str(ticket.id) not in read_file_string:
                    self._sl.send_message(ticket)
                    fl.write("  " + str(ticket.id))

        fl.close()
        return not_assigned_tickets_with_type

    def _get_lowest_ticket_count_suporter(self):
        sups = self._get_supporters()
        ticket_count = []

        for sup in sups:
            tickets = self._zenpy_client.search(type='ticket', group_id=21164867,
                                                     status=['open', 'pending'], assignee_id=sup.id)
            count = len(tickets)

            ticket_count.append({'nome': sup.name, 'count': count, 'id': sup.id})

        return min(ticket_count)

    def assign_tickets(self):
        for ticket in self._typing_tickets():
            sup = self._mc.get_suporters_by_zendesk_id(self._get_lowest_ticket_count_suporter()['id'])
            if sup:
                try:
                    ticket.assignee_id = sup['zendesk_id']
                    slack_id = sup['slack_id']
                    name = sup['name']
                    print(slack_id + " | " + name)
                    self._zenpy_client.tickets.update(ticket)
                    self._sl.notify_supporter(slack_id, name, ticket)
                except Exception as e:
                    print(e.args)

            elif not sup:
                print("No active agents to assign tickets")
