import anvil.server
import sys
import unittest


@anvil.server.callable
def server_auto_tests(verbosity=1):
  #unittest.main(exit=False)
  test_modules = ['helper_test', 'invite_test', 'relationship_test', 
                  'exchange_controller_test', 'network_controller_test',
                  'invite_fast_server_test', 'server_auto_test', 
                 ]
  test = unittest.TestLoader().loadTestsFromNames(test_modules)
  unittest.TextTestRunner(stream=sys.stdout, verbosity=verbosity).run(test)

  
@anvil.server.callable
def slow_tests(verbosity=2):
  #unittest.main(exit=False)
  test_modules = ['exchange_test', 'invite_server_test']
  test = unittest.TestLoader().loadTestsFromNames(test_modules)
  unittest.TextTestRunner(stream=sys.stdout, verbosity=verbosity).run(test)
