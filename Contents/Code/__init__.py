# -*- coding: utf-8 -*-

# Copyright (c) 2016, KOL
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from urlparse import urlparse
from updater import Updater

PREFIX = '/video/torrserver'

ART = 'art-default.jpg'
ICON = 'icon-default.png'
TITLE = 'TorrServer'

SERVER_RE = Regex('^(https|http)?://[^/:]+(:[0-9]{1,5})?$')


def Start():
    HTTP.CacheTime = 0


def ValidatePrefs():
    if (ValidateServer()):
        return MessageContainer(
            header=u'%s' % L('Success'),
            message=u'%s' % L('Preferences was changed')
        )
    else:
        return MessageContainer(
            header=u'%s' % L('Error'),
            message=u'%s' % L('Bad server address')
        )


def ValidateServer():
    return Prefs['server'] and SERVER_RE.match(Prefs['server'])


def GetLink(file):
    if 'Play' in file:
        return file['Play']
    return file['Link']


@handler(PREFIX, TITLE, thumb=ICON)
def MainMenu():

    oc = ObjectContainer(title2=TITLE, no_cache=True)

    Updater(PREFIX+'/update', oc)

    if not ValidateServer():
        return MessageContainer(
            header=u'%s' % L('Error'),
            message=u'%s' % L('Please specify server address in plugin preferences')
        )

    items = GetItems()

    if not items:
        return NoContents()

    server = GetServerUrl()
    for item in items:
        if len(item['Files']) > 1:
            oc.add(DirectoryObject(
                key=Callback(
                    List,
                    hash=item['Hash']
                ),
                title=u'%s' % item['Name']
            ))
        else:
            file = item['Files'][0]
            oc.add(GetVideoObject(server+GetLink(file), file['Name']))

    return oc


@route(PREFIX + '/list')
def List(hash):

    found = False
    items = GetItems()

    if not items:
        return NoContents()

    for item in items:
        if item['Hash'] == hash:
            found = True
            break

    if not found:
        return NoContents()

    oc = ObjectContainer(
        title2=u'%s' % item['Name'],
        replace_parent=False,
    )

    server = GetServerUrl()
    for file in item['Files']:
        oc.add(GetVideoObject(server+GetLink(file), file['Name']))

    if not len(oc):
        return NoContents()

    return oc


@route(PREFIX + '/play')
def VideoPlay(uri, title, **kwargs):
    return ObjectContainer(
        objects=[GetVideoObject(uri, title)],
        content=ContainerContent.GenericVideos
    )


def GetVideoObject(uri, title):
    uri = u'%s' % uri
    title = u'%s' % title
    return VideoClipObject(
        key=Callback(
            VideoPlay,
            uri=uri,
            title=title
        ),
        rating_key=uri,
        title=title,
        source_title=TITLE,
        items=[
            MediaObject(
                parts=[PartObject(key=uri)],
                container=Container.MP4,
                video_codec=VideoCodec.H264,
                audio_codec=AudioCodec.AAC,
                optimized_for_streaming=True
            )
        ]
    )


def GetItems():
    try:
        res = JSON.ObjectFromURL(GetServerUrl()+'/torrent/list', method='POST')
    except Exception as e:
        Log.Error(u'%s' % e)
        return None

    if not len(res):
        return None

    return res


def GetServerUrl():
    url = Prefs['server']
    if url[-1] == '/':
        return url[0:-1]
    return url


def NoContents():
    return ObjectContainer(
        header=u'%s' % L('Error'),
        message=u'%s' % L('No entries found')
    )
