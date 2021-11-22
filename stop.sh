#!/bin/bash

ps aux | grep -ie simplerelay.py | grep -v grep | awk '{print $2}' | xargs kill -9
