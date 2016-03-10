# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2016, Oracle and/or its affiliates. All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_log import log as logging

from neutron.agent.linux import utils

LOG = logging.getLogger(__name__)


class PacketFilter(object):
    '''Wrapper around Solaris pfctl(1M) command'''

    def __init__(self, anchor_name):
        '''All the PF rules/anchors will be placed under anchor_name.

        An anchor is a collection of rules, tables, and other anchors. They
        can be nested which allows PF rulesets to be chained together.

        Anchor names are always specified as absolute path starting from the
        root or main ruleset. For examples:

            _auto/neutron:l3:agent/l3eb1b8d0e7_1_0
            _auto/neutron:l3:agent/l3i45b26bf5_2_0/normal
            _auto/neutron:l3:agent/l3i45b26bf5_2_0/pbr

        If the root_anchor_path is set to _auto/neutron:l3:agent, then all
        the methods in this class will operate under that root anchor.
        '''
        self.root_anchor_path = anchor_name

    def _get_anchor_path(self, subanchors):
        if subanchors:
            return '%s/%s' % (self.root_anchor_path, '/'.join(subanchors))

        return self.root_anchor_path

    def add_nested_anchor_rule(self, parent_anchor, child_anchor,
                               anchor_option=None):
        """Adds an anchor rule that evaluates nested anchors.

        Adds child_anchor rule with anchor_option (if any) under parent_anchor.
        If parent_anchor is None, then the root_anchor_path will be used. An
        anchor rule (anchor "blah/*") tells PF to evaluate all the anchors and
        rules under 'blah'.

        pfctl(1M) doesn't provide a way to update ruleset under an anchor, so
        we need to always read the existing rules and add a new rule or
        remove an exisitng rule.
        """
        anchor_path = self._get_anchor_path(parent_anchor)
        existing_anchor_rules = self.list_anchor_rules(parent_anchor)
        LOG.debug(_('Existing anchor rules %s under %s') %
                  (existing_anchor_rules, anchor_path))
        for rule in existing_anchor_rules:
            if child_anchor in rule:
                LOG.debug(_('Anchor rule %s already exists') % rule)
                return
        anchor_rule = 'anchor "%s/*"' % child_anchor
        if anchor_option:
            anchor_rule = anchor_rule + " " + anchor_option
        existing_anchor_rules.append(anchor_rule)
        process_input = '%s\n' % '\n'.join(existing_anchor_rules)
        cmd = ['/usr/bin/pfexec', '/usr/sbin/pfctl', '-a', anchor_path,
               '-f', '-']
        LOG.debug(_('Running: %s') % ' '.join(cmd))
        utils.execute(cmd, process_input=process_input)

    def remove_nested_anchor_rule(self, parent_anchor, child_anchor):
        """ Removes an anchor rule that evaluates nested anchors.

        pfctl(1M) doesn't provide a way to update ruleset under an anchor, so
        we need to always read the existing rules and add a new rule or
        remove an exisitng rule.
        """
        anchor_path = self._get_anchor_path(parent_anchor)
        existing_anchor_rules = self.list_anchor_rules(parent_anchor)
        LOG.debug(_('Existing anchor rules %s under %s') %
                  (existing_anchor_rules, anchor_path))
        for rule in existing_anchor_rules:
            if child_anchor in rule:
                break
        else:
            LOG.debug(_('Anchor rule %s does not exist') % rule)
            return
        existing_anchor_rules.remove(rule)
        process_input = '%s\n' % '\n'.join(existing_anchor_rules)
        cmd = ['/usr/bin/pfexec', '/usr/sbin/pfctl', '-a', anchor_path,
               '-f', '-']
        LOG.debug(_('Running: %s') % ' '.join(cmd))
        utils.execute(cmd, process_input=process_input)

    def list_anchor_rules(self, subanchors=None):
        anchor_path = self._get_anchor_path(subanchors)
        cmd = ['/usr/bin/pfexec', '/usr/sbin/pfctl', '-a', anchor_path, '-sr']
        LOG.debug(_('Running: %s') % " ".join(cmd))
        stdout = utils.execute(cmd)
        anchor_rules = []
        for anchor_rule in stdout.strip().splitlines():
            anchor_rules.append(anchor_rule.strip())
        return anchor_rules

    def list_anchors(self, subanchors=None):
        anchor_path = self._get_anchor_path(subanchors)
        cmd = ['/usr/bin/pfexec', '/usr/sbin/pfctl', '-a', anchor_path, '-sA']
        LOG.debug(_('Running: %s') % " ".join(cmd))
        stdout = utils.execute(cmd)
        anchors = []
        for anchor in stdout.strip().splitlines():
            anchors.append(anchor.strip())
        return anchors

    def add_table(self, name, subanchors=None):
        anchor_path = self._get_anchor_path(subanchors)
        cmd = ['/usr/bin/pfexec', '/usr/sbin/pfctl', '-a', anchor_path,
               '-t', name, '-T', 'add']
        LOG.debug(_('Running: %s') % " ".join(cmd))
        utils.execute(cmd)

    def add_table_entry(self, name, cidrs, subanchors=None):
        anchor_path = self._get_anchor_path(subanchors)
        cmd = ['/usr/bin/pfexec', '/usr/sbin/pfctl', '-a', anchor_path,
               '-t', name, '-T', 'add']
        cmd.extend(cidrs)
        LOG.debug(_('Running: %s') % " ".join(cmd))
        utils.execute(cmd)

    def table_exists(self, name, subanchors=None):
        anchor_path = self._get_anchor_path(subanchors)
        try:
            cmd = ['/usr/bin/pfexec', '/usr/sbin/pfctl', '-a', anchor_path,
                   '-t', name, '-T', 'show']
            utils.execute(cmd)
        except:
            return False
        return True

    def remove_table(self, name, subanchors=None):
        if not self.table_exists(name, subanchors):
            LOG.debug(_('Table %s does not exist hence returning without '
                      'deleting') % name)
            return
        anchor_path = self._get_anchor_path(subanchors)
        cmd = ['/usr/bin/pfexec', '/usr/sbin/pfctl', '-a', anchor_path,
               '-t', name, '-T', 'delete']
        LOG.debug(_('Running: %s') % " ".join(cmd))
        utils.execute(cmd)

    def remove_table_entry(self, name, cidrs, subanchors=None):
        if not self.table_exists(name, subanchors):
            LOG.debug(_('Table %s does not exist hence returning without '
                      'deleting') % name)
            return
        anchor_path = self._get_anchor_path(subanchors)
        cmd = ['/usr/bin/pfexec', '/usr/sbin/pfctl', '-a', anchor_path,
               '-t', name, '-T', 'delete']
        cmd.extend(cidrs)
        LOG.debug(_('Running: %s') % " ".join(cmd))
        utils.execute(cmd)

    def add_rules(self, rules, subanchors=None):
        anchor_path = self._get_anchor_path(subanchors)
        process_input = '\n'.join(rules) + '\n'
        cmd = ['/usr/bin/pfexec', '/usr/sbin/pfctl', '-a', anchor_path,
               '-f', '-']
        LOG.debug(_('Running: %s with input %s') % (" ".join(cmd),
                                                    process_input))
        utils.execute(cmd, process_input=process_input)

    def _get_rule_label(self, rule):
        if 'label' not in rule:
            return None
        keywords = rule.split(' ')
        for i, keyword in enumerate(keywords):
            if keyword == 'label':
                break
        return keywords[i + 1]

    def remove_anchor(self, subanchors=None):
        anchor_path = self._get_anchor_path(subanchors)

        # retrieve all the labels for rules, we will delete the state
        # after removing the rules
        cmd = ['/usr/bin/pfexec', '/usr/sbin/pfctl', '-a', anchor_path, '-sr']
        LOG.debug(_('Running: %s') % " ".join(cmd))
        stdout = utils.execute(cmd)
        labels = []
        for rule in stdout.strip().splitlines():
            label = self._get_rule_label(rule.strip())
            if label:
                labels.append(label)

        # delete the rules and tables
        cmd = ['/usr/bin/pfexec', '/usr/sbin/pfctl', '-a', anchor_path,
               '-F', 'all']
        LOG.debug(_('Running: %s') % " ".join(cmd))
        utils.execute(cmd)

        # clear the state
        for label in labels:
            cmd = ['/usr/bin/pfexec', '/usr/sbin/pfctl', '-k', 'label',
                   '-k', label]
            LOG.debug(_('Running: %s') % " ".join(cmd))
            utils.execute(cmd)

    def _get_relative_nested_anchors(self, anchorname):
        # anchor name always come with absolute path, so we need to
        # remove the root anchor name to get relative path
        subanchors = anchorname.split('/')
        for anchor in self.root_anchor_path.split('/'):
            if anchor in subanchors:
                subanchors.remove(anchor)
        return subanchors

    def remove_anchor_recursively(self, subanchors=None):
        anchor_path = self._get_anchor_path(subanchors)
        cmd = ['/usr/bin/pfexec', '/usr/sbin/pfctl', '-a', anchor_path, '-sA']
        LOG.debug(_('Running: %s') % ' '.join(cmd))
        stdout = utils.execute(cmd)
        if not stdout.strip():
            return

        # we have nested anchors to remove so make recursive calls
        for nested_anchor in stdout.strip().splitlines():
            nested_anchor = nested_anchor.strip()
            if not nested_anchor:
                continue
            anchor_list = self._get_relative_nested_anchors(nested_anchor)
            self.remove_anchor_recursively(anchor_list)
            self.remove_anchor(anchor_list)
        anchor_list = self._get_relative_nested_anchors(anchor_path)
        self.remove_anchor(anchor_list)
