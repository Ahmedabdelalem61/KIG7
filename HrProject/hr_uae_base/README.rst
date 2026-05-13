===========
HR UAE Base
===========

Foundation module for the HR UAE Admin platform.

Provides:

* UAE working calendar (Sat-Thu, 8h, ``Asia/Dubai`` timezone)
* AED currency activation and auto-application to UAE companies
* UAE public holidays seeded as global time-off on the UAE calendar
* Security groups: ``User``, ``Document Owner``, ``Finance``, ``HR Manager``, ``Management``
* Root menu ``HR UAE Admin`` with placeholders for all phase-2+ menus

This module is the dependency root of every other ``hr_uae_*`` module and is
installed automatically by the meta module ``hr_uae_app``.
