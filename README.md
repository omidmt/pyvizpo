### pyvizpo Tableau VizPortal API lib in python

This is python lib to access vizportal api of Tableau that provide more options than default exposed rest api.

Since it uses a non-standard api, future version of tableau may not work correctly with this library.\

It is tested with Tableau 10 Vizportal API.

Implemented operations:

- generatePublicKey
- login
- setEnabledStatusForSchedules


```python
from pyvizpo import VizPortalApi, VizPortalError
import logging

tab_server = VizPortalApi('10.0.0.1', 80)

try:
    logging.basicConfig(level=logging.DEBUG)
    tab_server.login( 'my_username', 'my_password')
    tab_server.disable_schedule(1)

except VizPortalError as e:
    print 'VizPortal api call failed: {}'.format(e.message)
```