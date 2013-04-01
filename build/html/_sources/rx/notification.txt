:mod:`notification`
======================

.. module:: rx.notification
   :synopsis: Notification implementations.

.. **Source code:** :source:`rx/notification.py`

Notifications are used to record which events have happend. They are
most useful for testing where one wants to schedule some notifications
at a specific time and test if the operator reacted as expected.

.. autoclass:: Notification
	:members:

	.. staticmethod:: createOnNext(value)

    	Creates an :class:`OnNextNotification` that yields ``value``.

	.. staticmethod:: createOnError(exception)

    	Creates an :class:`OnErrorNotification` that yields ``exception``.

	.. staticmethod:: createOnCompleted()

    	Creates an :class:`OnCompletedNotification`.

.. autoclass:: OnNextNotification
	:members:

.. autoclass:: OnErrorNotification
	:members:

.. autoclass:: OnCompletedNotification
	:members:
