#!/usr/bin/env python3
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Test cases for enabled APIs."""

import os
import unittest

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

# Set dunder unittest in the global scope for pretty unit test results
__unittest = True

class TestEnabledAPIs(unittest.TestCase):
  """Test cases for enabled APIs. Note that this test requires the PROJECT_ID
  environment variable to be set."""

  def setUp(self) -> None:
    """Call super class' setup and define some variables."""
    super().setUp()
    self.project_id = os.getenv('PROJECT_ID', 'my-project')
    self.enabled_apis = {'assuredworkloads.googleapis.com',
                         'cloudkms.googleapis.com',
                         'compute.googleapis.com',
                         'iam.googleapis.com',
                         'iamcredentials.googleapis.com',
                         'oslogin.googleapis.com',
                         'serviceusage.googleapis.com',
                         'cloudresourcemanager.googleapis.com'}

  def test_enabled_apis(self):
    """Testing to see if any APIs need to be flipped."""
    # Get application-default credentials and initialize API client
    credentials = GoogleCredentials.get_application_default()
    project = 'projects/' + self.project_id
    service = discovery.build('serviceusage', 'v1', credentials=credentials)
    try:
      apis = {'ENABLED': [], 'DISABLED': []}
      # Set the next page token to 'first' just so we know not to include that
      # argument in the first services().list() call
      next_page = 'first'
      # Iterate over pages of API responses
      while next_page:
        if next_page == 'first':
          request = service.services().list(parent=project)
        else:
          request = service.services().list(parent=project, pageToken=next_page)
        response = request.execute()
        if 'nextPageToken' in response:
          next_page = response['nextPageToken']
        else:
          next_page = False
        # Now read the enabled and disabled APIs and put them in the appropriate
        # list
        services = response.get('services')
        for index in range(len(services)):
          item = services[index]
          if item.get('config').get('name'):
            apis[item['state']].append(item['config']['name'])
        # Assert that the expected enabled APIs are equal to the actual enabled
        # APIs
      self.assertSetEqual(self.enabled_apis, set(apis['ENABLED']),
                          'APIs that need to be enabled or disabled')
    except Exception as e:
      raise e
