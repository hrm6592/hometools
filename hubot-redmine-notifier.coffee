# Notifies about Redmine creating and updating tickets.
#
# Dependencies:
#   "url": ""
#   "querystring": ""
#
# Configuration:
#   Install [Redmine Webhook Plugin](https://github.com/suer/redmine_webhook) to your Redmine.
#   Add hubot's endpoint to Redmine Project - Settings - WebHook - URL `http://<hubot-host>:<hubot-port>/hubot/redmine-notify?room=<room>` (see Screenshot)
#
# Commands:
#   None
#
# URLS:
#   POST /hubot/redmine-notify?room=<room>
#
# Author:
#   tenten0213

'use strict'

url = require('url')
querystring = require('querystring')
util = require('util')

# Preparing log stream.
fs = require('fs')
Log = require('log')
logger = new Log('notice',
    fs.createWriteStream('/var/log/hubot/hubot.log',
        {flags: 'a'}))

class RedmineNotifier
  constructor: (robot) ->
    @robot = robot

  error: (err, body) ->
    logger.error "redmine-notify error: #{err.message}. Data: #{util.inspect(body)}"
    console.log "redmine-notify error: #{err.message}. Data: #{util.inspect(body)}"
    logger.error err.stack
    console.log err.stack

  dataMethodJSONParse: (req,data) ->
    return false if typeof req.body != 'object'
    ret = Object.keys(req.body).filter (val) ->
      val != '__proto__'

    try
      if ret.length == 1
        return JSON.parse ret[0]
    catch err
      return false

    return false

  dataMethodRaw: (req) ->
    return false if typeof req.body != 'object'
    return req.body

  process: (req, res) ->
    query = querystring.parse(url.parse(req.url).query)

    res.end('')

    envelope = {}
    envelope.user = {}
    envelope.user.room = envelope.room = query.room if query.room

    data = null

    filterChecker = (item, callback) ->
      return if data

      ret = item(req)
      if (ret)
        data = ret
        return true

    [@dataMethodJSONParse, @dataMethodRaw].forEach(filterChecker)

    payload = data.payload
    issue = payload.issue
    project = issue.project.name
    author = issue.author.login
    action = payload.action
    tracker = issue.tracker.name
    issueId = issue.id
    issueSubject = issue.subject
    status = issue.status.name
    assignee = unless issue.assignee? then "" else issue.assignee.login
    priority = issue.priority.name
    issueUrl = payload.url
    message = """
              [#{project}] #{author} #{action} #{tracker}##{issueId}
              Subject: #{issueSubject}
              Status: #{status}
              Priority: #{priority}
              Assignee: #{assignee}
              URL: #{issueUrl}
              """

    @robot.send envelope, message

module.exports = (robot) ->
  robot.redmine_notifier = new RedmineNotifier robot

  robot.router.post "/hubot/redmine-notify", (req, res) ->
    robot.redmine_notifier.process req, res
