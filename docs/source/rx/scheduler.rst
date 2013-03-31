:mod:`scheduler`
======================

.. module:: rx.scheduler
	:synopsis: Scheduler implementations.

.. **Source code:** :source:`rx/notification.py`

Schedulers are the main source of concurrency in RxPython. Every action that happens
either periodically, concurrently, or is timed for later execution should be scheduled
by the correct :class:`Scheduler` implementation. Some Schedulers as the
:attr:`Scheduler.currentThread` allow for cooperative multitasking, others like the
:attr:`Scheduler.default` are used for scheduling on different threads and the
ThreadPool.

Instances for Schedulers should NEVER be created manually but instead the static
properties on the :class:`Scheduler` class should be used to get an instance.

.. autoclass:: Scheduler

	.. method:: now

    	Returns the current time.

	.. method:: catchException(handler)

		Returns a :class:`Scheduler` that invokes the handler function
		if an exception gets raised. If the handler returns False the
		Exception is reraised.

	**Long running scheduling**

	.. attribute:: isLongRunning

		Returns True if the scheduler implementation supports long running
		scheduling via :meth:`scheduleLongRunning` and
		:meth:`scheduleLongRunningWithState`

	.. method:: scheduleLongRunning(action)

		Schedules ``action`` as long running which in the current implementation
		runs the action on a separate Thread. The action gets as parameter its
		own :class:`rx.disposable.Cancelable` on which it can check, if it got
		disposed.

		Actions scheduled as long running are guaranteed to run even if the got
		canceled befor running.

	.. method:: scheduleLongRunningWithState(state, action)

		Schedules ``action`` as long running which in the current implementation
		runs the action on a separate Thread. The action gets as parameter
		``state`` and its own :class:`rx.disposable.Cancelable` on which it can check,
		if it got disposed.

		Actions scheduled as long running are guaranteed to run even if the got
		canceled befor running.

	**Periodic Scheduling**

	.. method:: schedulePeriodicWithState(state, period, action)

		Schedules ``action`` for periodic execution every ``period``.

	.. method:: schedulePeriodicWithState(state, period, action)

		Schedules ``action`` for periodic execution every ``period``. The
		action gets as parameter ``state`` and should return the new state
		that is used on the next periodic invocation.

	**Immediate Scheduling**

	.. method:: schedule(action)

		Schedules ``action`` for immediate execution. ``action`` receives
		as parameter the scheduler.

	.. method:: scheduleWithState(state, action)

		Schedules ``action`` for immediate execution. ``action`` receives
		as parameter the scheduler and ``state``.

	**Relative time scheduling**

	.. method:: scheduleWithRelative(dueTime, action)

		Schedules ``action`` for execution after ``dueTime``.
		``action`` receives as parameter the scheduler.

	.. method:: scheduleWithRelativeAndState(state, dueTime, action)

		Schedules ``action`` for execution after ``dueTime``.
		``action`` receives as parameter the scheduler and ``state``.

	**Absolute time scheduling**

	.. method:: scheduleWithAbsolute(dueTime, action)

		Schedules ``action`` for execution at ``dueTime``.
		``action`` receives as parameter the scheduler.

	.. method:: scheduleWithAbsoluteAndState(state, dueTime, action)

		Schedules ``action`` for execution at ``dueTime``.
		``action`` receives as parameter the scheduler and ``state``.

	**Recursive scheduling**

	.. method:: scheduleRecursive(action)

		Schedules ``action`` immediately for recursive execution.
		``action`` receives as parameter the continuation function to
		schedule itself recursively.

	.. method:: scheduleRecursiveWithState(state, action)

		Schedules ``action`` immediately for recursive execution.
		``action`` receives as parameter the state and the continuation function
		to schedule itself recursively. The parameter given to the
		continuation function is the state for the next invocation of
		``action``.

	.. method:: scheduleRecursiveWithRelative(dueTime, action)

		Schedules ``action`` for recursive execution after ``dueTime``.
		``action`` receives as parameter the continuation function to
		schedule itself recursively.

	.. method:: scheduleRecursiveWithRelativeAndState(state, dueTime, action)

		Schedules ``action`` for recursive execution after ``dueTime``.
		``action`` receives as parameter the state and the continuation function
		to schedule itself recursively. The parameter given to the
		continuation function is the state for the next invocation of
		``action``.

	.. method:: scheduleRecursiveWithAbsolute(dueTime, action)

		Schedules ``action`` for recursive execution at ``dueTime``.
		``action`` receives as parameter the continuation function to
		schedule itself recursively.

	.. method:: scheduleRecursiveWithAbsoluteAndState(state, dueTime, action)

		Schedules ``action`` for recursive execution at ``dueTime``.
		``action`` receives as parameter the state and the continuation function
		to schedule itself recursively. The parameter given to the
		continuation function is the state for the next invocation of
		``action``.

	**Static attributes of scheduler instances**

	.. attribute:: immediate

		A :class:`Scheduler` that runs all scheduled actions immediately.
		It does not support long running and periodic scheduling.

	.. attribute:: currentThread

		A :class:`Scheduler` that keeps a queue of all scheduled actions.
		It does not support long running and periodic scheduling but
		allows for cooperative scheduling which means that for example a
		generator and a consumer could be scheduled at the same time and
		both would run concurrently.

	.. attribute:: default

		A :class:`Scheduler` that supports all scheduling operations.
		It is the default scheduler and should be used whenever no particular
		reason exists to use an other scheduler implementation.
