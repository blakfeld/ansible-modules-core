#!/usr/bin/python
#coding: utf-8 -*-

# (c) 2013-2014, Christian Berendt <berendt@b1-systems.de>
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

import re
from ansible.module_utils.basic import *

DOCUMENTATION = """
---
module: apache2_site
version_added: 2.1
author: "Corwin Brown (@blakfeld)"
short_description: enables/disables a site in the Apache2 webeerver.
description:
   - Enables or disables a specified site in the Apache2 webserver.
options:
   name:
     description:
        - name of the site to enable/disable
     required: true
   state:
     description:
        - indicate the desired state of the resource
     choices: ['present', 'absent']
     default: present

requirements: ["a2ensite","a2dissite"]
"""

EXAMPLES = """
# enables the Apache2 site 000-default
- apache2_site:
    name: '000-default'
    state:present

# disables the Apache2 site 000-default
- apache2_module:
    name: '000-default'
    state: absent
"""

RETURNS = """
result:
    description: Textual summary on if the module completed successfully.
    returned: success
    type: string
    sample: 'Enabled'
"""


def _get_binary(binary_name, module):
    """
    Get the path of the specified binary.

    Args:
        binary_name (str):          Name of binary to search for.
        module (Ansible Module):    Ansible Module instance for this module.

    Returns:
        str -- Path to Binary.
    """

    binary = module.get_bin_path(binary_name)
    if binary is None:
        module.fail_json(
            msg='a2ensite is not found. Perhaps this system does not use '
                'a2enmod to manage Apache'
        )

    return binary


def _disable_site(module):
    """
    Shells out and calls a2dissite and parses the output.

    Args:
        module (AnsibleModule):     Ansible Module instance for this module.
    """

    a2dissite_binary = _get_binary('a2dissite', module)

    site_name = module.params['name']
    result, stdout, stderr = module.run_command('{a2dissite} {site_name}'.format(
        a2dissite=a2dissite_binary,
        site_name=site_name,
        )
    )
    if re.match(r'.*\b{0} already disabled'.format(site_name), stdout, re.S | re.M):
        module.exit_json(changed=False, result='Success')
    elif result != 0:
        module.fail_json(msg='Failed to disable site {0}: {1}'.format(site_name, stdout))
    else:
        module.exit_json(changed=True, result='Disabled')


def _enable_site(module):
    """
    Shells out and calls a2ensite and parses the output.

    Args:
        module (AnsibleModule):     Ansible Module instance for this module.
    """

    a2ensite_binary = _get_binary('a2ensite', module)

    site_name = module.params['name']
    result, stdout, stderr = module.run_command('{a2ensite} {site_name}'.format(
        a2ensite=a2ensite_binary,
        site_name=site_name,
        )
    )
    if re.match(r'.*\b{0} already enabled'.format(site_name), stdout, re.S | re.M):
        module.exit_json(changed=False, result='Success')
    elif result != 0:
        module.fail_json(msg='Failed to enable site {0}: {1}'.format(site_name, stdout))
    else:
        module.exit_json(changed=True, result='Enabled')


def main():
    """
    Main
    """

    # Parse Ansible inputs
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            state=dict(default='present', choices=['absent', 'present']),
        )
    )

    site_state = module.params['state']
    if site_state == 'present':
        _enable_site(module)
    elif site_state == 'absent':
        _disable_site(module)


if __name__ == '__main__':
    main()
