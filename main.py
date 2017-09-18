# Copyright 2016 Google Inc. All rights reserved.
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

"""This is a sample Hello World API implemented using Google Cloud
Endpoints."""

# [START imports]
import endpoints
from protorpc import message_types
from protorpc import messages
from protorpc import remote
# [END imports]


# [START messages]
class SendReportRequest(messages.Message):
    location = messages.StringField(1)


class SendReportResponse(messages.Message):
    report_id = messages.StringField(1)
    
   
class RoadkillReportResponse(messages.Message):
    location = messages.StringField(1)
    timestamp = messages.StringField(2)
    
ROADKILL_RESOURCE = endpoints.ResourceContainer(
    message_types.VoidMessage,
    report_id=messages.StringField(2))
# [END messages]


# [START roadkill_api]
@endpoints.api(name='roadkill', version='v1')
class RoadkillApi(remote.Service):

    @endpoints.method(
        SendReportRequest,
        SendReportResponse,
        path='roadkill',
        http_method='POST',
        name='report_roadkill')
    def report_roadkill(self, request):
        report_id = 'some id'
        return SendReportResponse(report_id=report_id)

    @endpoints.method(
        ROADKILL_RESOURCE,
        RoadkillReportResponse,
        path='roadkill/{report_id}',
        http_method='GET',
        name='roadkill')
    def get_roadkill_report(self, request):
        resp = RoadkillReportResponse(location='location', timestamp='timestamp')
        return resp
# [END roadkill_api]


# [START api_server]
api = endpoints.api_server([RoadkillApi])
# [END api_server]
