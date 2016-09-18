#
# Copyright 2016 Robert Clark (clark@exiter.com)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import logging

import zonebot
from configparser import ConfigParser
from zonebot.commands import *

logging.basicConfig(level=logging.CRITICAL)
logging.getLogger("zonebot").disabled = True


def verify_command(words, config, user_id, expected):
    cmd = get_command(words=words, user_id=user_id, config=config)
    assert isinstance(cmd, expected), "Expected class %s, found %s" % (type(expected), type(cmd))


def test_help():
    verify_command(['help'], None, None, zonebot.commands.Help)


def test_unknown():
    verify_command(['unknown', 'command'], None, None, zonebot.commands.Unknown)


def test_weird_case():
    verify_command(['LiST', '    moniTorS   '], None, None, zonebot.commands.ListMonitors)


def test_permission_no_section():
    """ When there is no permission section, anyone can do anything. """

    Command._usermap['me'] = 'me'
    config = ConfigParser()

    config.remove_section('Permissions')

    # any permission
    verify_command(['help'], config, 'me', zonebot.commands.Help)

    # read permission
    verify_command(['list', 'monitors'], config, 'me', zonebot.commands.ListMonitors)

    # write permission
    verify_command(['enable', 'monitor', 'Blammo'], config, 'me', zonebot.commands.ToggleMonitor)
    verify_command(['disable', 'monitor', 'Blammo'], config, 'me', zonebot.commands.ToggleMonitor)

    # unknown command, never allowed
    verify_command(['something', 'else'], config, 'me', zonebot.commands.Unknown)


def test_permission_empty_section():
    """ When there is a permission section, but no entries, everyone gets read access. """
    Command._usermap['me'] = 'me'
    config = ConfigParser()

    config.remove_section('Permissions')
    config.add_section('Permissions')

    # any permission
    verify_command(['help'], config, 'me', zonebot.commands.Help)

    # read permission
    verify_command(['list', 'monitors'], config, 'me', zonebot.commands.ListMonitors)

    # write permission
    verify_command(['enable', 'monitor', 'Blammo'], config, 'me', zonebot.commands.Denied)
    verify_command(['disable', 'monitor', 'Blammo'], config, 'me', zonebot.commands.Denied)

    # unknown command, never allowed
    verify_command(['something', 'else'], config, 'me', zonebot.commands.Unknown)


def test_permission_read():
    """ 'read' permission is any command that is marked with 'read' """
    Command._usermap['me'] = 'me'
    config = ConfigParser()

    config.remove_section('Permissions')
    config.add_section('Permissions')
    config.set('Permissions', 'me', 'read')

    # any permission
    verify_command(['help'], config, 'me', zonebot.commands.Help)

    # read permission
    verify_command(['list', 'monitors'], config, 'me', zonebot.commands.ListMonitors)

    # write permission
    verify_command(['enable', 'monitor', 'Blammo'], config, 'me', zonebot.commands.Denied)
    verify_command(['disable', 'monitor', 'Blammo'], config, 'me', zonebot.commands.Denied)

    # unknown command, never allowed
    verify_command(['something', 'else'], config, 'me', zonebot.commands.Unknown)


def test_permission_write():
    """ 'write' permission is any command that is marked with 'write' """
    Command._usermap['me'] = 'me'
    config = ConfigParser()

    config.remove_section('Permissions')
    config.add_section('Permissions')
    config.set('Permissions', 'me', 'write')

    # any permission
    verify_command(['help'], config, 'me', zonebot.commands.Help)

    # read permission
    verify_command(['list', 'monitors'], config, 'me', zonebot.commands.Denied)

    # write permission
    verify_command(['enable', 'monitor', 'Blammo'], config, 'me', zonebot.commands.ToggleMonitor)
    verify_command(['disable', 'monitor', 'Blammo'], config, 'me', zonebot.commands.ToggleMonitor)

    # unknown command, never allowed
    verify_command(['something', 'else'], config, 'me', zonebot.commands.Unknown)


def test_permission_any():
    """ 'write' permission is any command that is marked with 'write' """
    Command._usermap['me'] = 'me'
    config = ConfigParser()

    config.remove_section('Permissions')
    config.add_section('Permissions')
    config.set('Permissions', 'me', 'any')

    # any permission
    verify_command(['help'], config, 'me', zonebot.commands.Help)

    # read permission
    verify_command(['list', 'monitors'], config, 'me', zonebot.commands.ListMonitors)

    # write permission
    verify_command(['enable', 'monitor', 'Blammo'], config, 'me', zonebot.commands.ToggleMonitor)
    verify_command(['disable', 'monitor', 'Blammo'], config, 'me', zonebot.commands.ToggleMonitor)

    # unknown command, never allowed
    verify_command(['something', 'else'], config, 'me', zonebot.commands.Unknown)


def test_permission_command():
    """ Permissions for a specific command only """

    Command._usermap['me'] = 'me'
    config = ConfigParser()

    config.remove_section('Permissions')
    config.add_section('Permissions')
    config.set('Permissions', 'me', 'enable monitor')

    # any permission
    verify_command(['help'], config, 'me', zonebot.commands.Help)

    # read permission
    verify_command(['list', 'monitors'], config, 'me', zonebot.commands.Denied)

    # write permission
    verify_command(['enable', 'monitor', 'Blammo'], config, 'me', zonebot.commands.ToggleMonitor)
    verify_command(['disable', 'monitor', 'Blammo'], config, 'me', zonebot.commands.Denied)

    # unknown command, never allowed
    verify_command(['something', 'else'], config, 'me', zonebot.commands.Unknown)


def test_permission_combined():
    """ command and read permission """

    Command._usermap['me'] = 'me'
    config = ConfigParser()

    config.remove_section('Permissions')
    config.add_section('Permissions')
    config.set('Permissions', 'me', '   read,     write')

    # any permission
    verify_command(['help'], config, 'me', zonebot.commands.Help)

    # read permission
    verify_command(['list', 'monitors'], config, 'me', zonebot.commands.ListMonitors)

    # write permission
    verify_command(['enable', 'monitor', 'Blammo'], config, 'me', zonebot.commands.ToggleMonitor)
    verify_command(['disable', 'monitor', 'Blammo'], config, 'me', zonebot.commands.ToggleMonitor)

    # unknown command, never allowed
    verify_command(['something', 'else'], config, 'me', zonebot.commands.Unknown)