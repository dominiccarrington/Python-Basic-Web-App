"""
Basic Python Web Application
Copyright (C) 2017 Dominic Carrington

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import time

class Timer:
    timers = {}
    @staticmethod
    def start(name):
        Timer.timers[name] = Timer.current_time()

    @staticmethod
    def stop(name):
        return Timer.current_time() - Timer.timers[name]

    @staticmethod
    def current_time():
        return int(round(time.time() * 1000))
