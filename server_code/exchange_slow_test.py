import unittest
from unittest.mock import Mock
import datetime
from anvil.tables import app_tables
import anvil.tables.query as q
from .misc_server_test import ADMIN, USER2, USER3
from . import request_test as rt
from empathy_chat import request_interactor as ri
from empathy_chat import request_gateway as rg
from empathy_chat import exchange_gateway as eg
from empathy_chat import exchange_interactor as ei
from empathy_chat import requests as rs
from empathy_chat import server_misc as sm
from empathy_chat import portable as port
from empathy_chat import exchanges as es
from empathy_chat import notifies as n
from anvil_extras.logging import TimerLogger

class TestExchangeGateway(unittest.TestCase):
  def setUp(self):
    self.request_records_saved = []
    self.request_rows_created = []
    self.exchange_records_saved = []
    self.exchange_rows_created = []
    self._email_send = n.email_send
    n.email_send = Mock()
    self._send_sms = n.send_sms
    n.send_sms = Mock()
  
  def test_exchange_record_save(self):
    prop = rt.prop_u2_2to3_now
    request = next(rs.prop_to_requests(prop))
    request_record = rg.RequestRecord(request)
    request_record.save()
    self.request_records_saved.append(request_record)
    request.request_id = request_record.record_id
    exchange = es.Exchange.from_exchange_prospect(rs.ExchangeProspect([request]))
    exchange_record = eg.ExchangeRecord(exchange)
    self.assertFalse(exchange_record.record_id)
    exchange_record.save()
    self.exchange_records_saved.append(exchange_record)
    self.assertTrue(exchange_record.record_id)
    exchange.exchange_id = exchange_record.record_id
    saved_exchange = eg.ExchangeRecord.from_id(exchange_record.record_id).entity
    for attribute in ['exchange_format', 
                      'room_code',
                      'current',
                      'start_dt',
                      'start_now',
                     ]:
      self.assertEqual(getattr(exchange, attribute), getattr(saved_exchange, attribute))
    for key in ['user_id',
                'request_id',
               ]:
      self.assertEqual(exchange.participants[0][key], saved_exchange.participants[0][key])
    self.assertEqual(saved_exchange.participants[0]['appearances'], [])
    for key in ['entered_dt',
                'slider_value',
                'video_embedded',
                'complete_dt',
               ]:
      self.assertEqual(saved_exchange.participants[0][key], None)

  def test_add_request_exchange_save(self):
    with TimerLogger("  test", format="{name}: {elapsed:6.3f} s | {msg}") as timer:
      prop1 = rt.prop_u2_2to3_in1hr_in2hr
      prop2 = rt.prop_uA_2to2_in1hr
      or_group1 = ri._add_request(USER2, prop1)
      timer.check("1st _add_request")
      or_group2 = ri._add_request(ADMIN, prop2)
      timer.check("2nd _add_request")
      requests = list(app_tables.requests.search(or_group_id=q.any_of(or_group1, or_group2)))
      self.request_rows_created.extend(requests)
      timer.check("grab request rows created")
      row_2hr = next((row for row in requests 
                      if row['start_dt'] - sm.now() > datetime.timedelta(hours=1.5)))
      self.assertFalse(row_2hr['current'])
      timer.check("check row_2hr")
      upcomings = list(eg.exchanges_by_user(USER2, records=True))
      self.exchange_records_saved.append(upcomings[0])
      self.assertEqual(len(upcomings), 1)
      timer.check("grab upcomings")
      match_dicts2 = ei.upcoming_match_dicts(USER2)
      match_dictsA = ei.upcoming_match_dicts(ADMIN)
      timer.check("grab match_dicts")
      self.assertEqual(len(match_dicts2[0]), 4)
      for key in match_dicts2[0]:
        if key != 'port_users':
          self.assertEqual(match_dicts2[0][key], match_dictsA[0][key])
    
  def tearDown(self):
    n.email_send = self._email_send
    n.send_sms = self._send_sms
    for row in self.request_rows_created + [rr._row for rr in self.request_records_saved]:
      row.delete()
    for row in self.exchange_rows_created + [er._row for er in self.exchange_records_saved]:
      for p_row in row['participants']:
        for a_row in p_row['appearances']:
          a_row.delete()
        p_row.delete()
      row.delete()
