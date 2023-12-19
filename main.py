#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 07:21:45 2022

@author: armsy326
"""

from app import app,socketio

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000,allow_unsafe_werkzeug=True)
  
