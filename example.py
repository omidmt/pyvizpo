from pyvizpo import VizPortalApi, VizPortalError
import logging

tab_server = VizPortalApi('10.0.0.1', 80)

try:
    logging.basicConfig(level=logging.DEBUG)
    tab_server.login( 'my_username', 'my_password')
    tab_server.disable_schedule(1)

except VizPortalError as e:
    print 'VizPortal api call failed: {}'.format(e.message)


