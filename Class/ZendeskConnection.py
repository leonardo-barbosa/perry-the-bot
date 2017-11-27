# coding: utf8
from zenpy import Zenpy
from Class import SlackConnection
from Class import MongoConnection
from Dicty import tags
from unidecode import unidecode
from datetime import datetime, timedelta
import time
import utilities
import os
import re

class ZendeskConnection:
    def __init__(self):
        self._creds = {
            'email': os.environ.get('ZENDESK_USER', None),
            'token': os.environ.get('ZENDESK_TOKEN', None),
            'subdomain': "pagarme"
        }
        self._zenpy_client = Zenpy(**self._creds)
        self._sl = SlackConnection.SlackConnection()
        self._mc = MongoConnection.MongoConnection()


    def _generate_comment(self, ticket):
        ticket_comments = ""
        for comment in self._zenpy_client.tickets.comments(ticket_id=ticket.id):
            ticket_comments += " " + str(comment)

        return self._remove_special_characters(ticket_comments)


    def _remove_special_characters(self, phrase):
        phrase = phrase.lower()
        return unidecode(phrase)

    def _word_in_text(self, word, text):
        if re.search(r'\b' + word + r'\b', text):
            return True
        return False


    def _tag_ticket(self, ticket):
        try:
            TAGS = tags.TAGS
            new_tags = []
            subject = self._remove_special_characters(ticket.subject)
            ticket_comments = self._generate_comment(ticket)
            description = self._remove_special_characters(ticket.description)
            content = subject + " " + ticket_comments + " " + description + " "
            for tag in TAGS:
                for word in TAGS[tag]:
                    if (self._word_in_text(word, content)) and (tag not in new_tags):
                        new_tags.append(tag)
            ticket.tags.extend(new_tags)
            self._zenpy_client.tickets.update(ticket)
        except Exception as e:
            print(e.args)


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


    def _get_yesterday_tickets(self):
        yesterday = datetime.now() - timedelta(days=2)
        yesterday_tickets = self._zenpy_client.search(type='ticket', created_after=yesterday.date(), group_id=21164867)
        support_tickets = [];
        for ticket in yesterday_tickets:
            support_tickets.append(ticket)

        return support_tickets


    def _get_ticket_count_supporter(self):
        sups = self._get_supporters()
        ticket_count = []

        for sup in sups:
            tickets = self._zenpy_client.search(type='ticket', group_id=21164867,
                                                status=['open', 'pending'], assignee_id=sup.id)
            count = len(tickets)

            ticket_count.append({'nome': sup.name, 'count': count, 'id': sup.id})

        print('Active supporters: \n' + str(ticket_count))

        return ticket_count


    def tag_yesterday_tickets(self):
        yesterday_tickets = self._get_yesterday_tickets()
        tagged_tickets = [];
        for ticket in yesterday_tickets:
            self._tag_ticket(ticket)
            tagged_tickets.append(ticket.id)
        print('Tagged tickets: ' + ''.join( str(tagged_tickets) ) )


    def assign_tickets(self):
        sups = self._get_ticket_count_supporter()
        # Send ticket type message through slack
        tickets = self._typing_tickets()
        if sups:
            if len(tickets) > 0:
                for ticket in tickets:
                    #  Get lowest ticket count supporter
                    lowest_ticket_count_sup = None
                    for count in sups:
                        if not lowest_ticket_count_sup:
                            lowest_ticket_count_sup = count
                        elif count['count'] < lowest_ticket_count_sup['count']:
                            lowest_ticket_count_sup = count

                    sup = self._mc.get_supporters_by_zendesk_id(lowest_ticket_count_sup['id'])
                    try:
                        # Assign the ticket
                        ticket.assignee_id = sup['zendesk_id']
                        slack_id = sup['slack_id']
                        name = sup['name']
                        print(slack_id + " | " + name)
                        self._zenpy_client.tickets.update(ticket)

                        # Notify the supporter on slack
                        self._sl.notify_supporter(slack_id, name, ticket)

                        # Increase the ticket count for the agent who got it
                        for agent in sups:
                            if agent['id'] == lowest_ticket_count_sup['id']:
                                agent['count'] += 1

                    except Exception as e:
                        print(e.args)
            elif len(tickets) <= 0:
                print("No tickets to assign.")
        elif not sups:
            print("No active agents to assign tickets.")

