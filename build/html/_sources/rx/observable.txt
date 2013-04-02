:mod:`observable`
======================

.. module:: rx.observable
   :synopsis: Observable implementation.

.. **Source code:** :source:`rx/observable.py`

Observables are similar to iterables in that they yield values until
either an Exception gets raised or the sequence completes. But in contrast
to iterables one can not explicitly request an :class:`Observable` to yield
the next value but the next value will be yielded when it is generated.

Thus a good example for an Observable is an event. Every time the event
gets raised, the Observable produces its next value and sends it down
the pipeline.

The power of RxPython comes from the fact that it provides a set of Operators
to create, merge, split and await Observables. The operators are named like
SQL keywords on purpouse to make the library easier to use and understand.

In the following documentation the operators are split up into specific domains
like aggregation, blocking and multiple to make the overall navigation easier.

Some most of the names of the operators are directly ported from the C# original
implementation, some were renamed to integrate with the python native names
more directly. It is clear that many of the things are not implemented in the
most ideomatic way. This is just because the first milestone was to get the
whole library working. Further optimisations can be made later.


.. class:: Observable

	.. method:: subscribe(observer)
				subscribe([onNext=None, onError=None, onCompleted=None])

		If no observer is provided but instead any of the methods ``onNext``,
		``onError``, or ``onCompleted`` an anonymous
		:class:`Observer <rx.observer.Observer>` will be created.

		Subscribes the observer for the sequence.


.. class:: AnonymouseObservable(subscribe)

	Represents an :class:`Observable` that calls ``subscribe``
	every time an :class:`Observer <rx.observer.Observer>` subscribes.

	The observer will be passed as parameter to ``subscribe``.

	``subscribe`` should return a
	:class:`Disposable <rx.disposable.Disposable>`.


.. class:: ConnectableObservable(source, subject)

	Represents an :class:`Observable` that can be connected and disconnected.

	.. method:: subscribe(observer)
				subscribe([onNext=None, onError=None, onCompleted=None])

		Returns the result of subscribing to ``subject``.

	.. method:: connect()

		Subscribes ``subject`` to ``source`` and returns
		:class:`Disposable <rx.disposable.Disposable>` to cancel
		the connection.

.. class:: GroupObservable

	Represents an :class:`Observable` that has a key. Most likely it
	resulted from a groupby call.

	.. attribute:: key

		The key of this :class:`Observable`.


Aggregation
-----------

.. class:: Observable

	.. method:: aggregate(seed, accumulator[, resultSelector=identity])

		Aggregates the values of the :class:`Observable`. When the source
		completes, ``resultSelector(accumulation)`` is yielded as next value.

	.. method:: all(predicate)

		Yields True if ``predicate(value) == True`` for all values.

	.. method:: any([predicate=truePredicate])

		Yields True if ``predicate(value) == True`` for any value.

	.. method:: average([selector=identity])

		Yields the average value of ``selector(value)`` for all values.

	.. method:: contains(value[, equals=defaultEquals])

		Yields True if ``equals(value, onNextValue) == True`` for any value.

	.. method:: count([predicate=truePredicate])

		Yields how often ``predicate(value) == True``.

	.. method:: elementAt(index)

		Yields the value at index ``index`` or completes
		exceptionally with :class:`IndexError`.

	.. method:: elementAtOrDefault(index[, default=None])

		Yields the value at index ``index`` or ``default``.

	.. method:: firstAsync([predicate=truePredicate])

		Yields the first value where ``predicate(value) == True``
		or completes exceptionally with
		:class:`InvalidOperationException("No elements in observable") <rx.exceptions.InvalidOperationException>`.

	.. method:: firstAsyncOrDefault([predicate=truePredicate, default=None])

		Yields the first value where ``predicate(value) == True``
		or ``default``.

	.. method:: isEmpty()

		Yields True if the current :class:`Observable` contains no values.

	.. method:: lastAsync([predicate=truePredicate])

		Yields the last value where ``predicate(value) == True``
		or completes exceptionally with
		:class:`InvalidOperationException("No elements in observable") <rx.exceptions.InvalidOperationException>`.

	.. method:: lastAsyncOrDefault([predicate=truePredicate, default=None])

		Yields the last value or default.

	.. method:: max([compareTo=defaultCompareTo])

		Yields the maximum value. The maximum value is the value
		where ``compareTo(value, currentMax)`` returns 1 at
		the end or completes exceptionally with
		:class:`InvalidOperationException("No elements in observable") <rx.exceptions.InvalidOperationException>`.

	.. method:: maxBy(keySelector[, compareTo=defaultCompareTo])

		Yields the maximum value. The maximum value is the value
		where ``compareTo(keySelector(value), currentMax)``
		returns 1 at the end.

	.. method:: min([compareTo=defaultCompareTo])

		Yields the minimum value. The minimum value is the value
		where ``compareTo(value, currentMin)`` returns -1 at
		the end or completes exceptionally with
		:class:`InvalidOperationException("No elements in observable") <rx.exceptions.InvalidOperationException>`.

	.. method:: minBy(keySelector[, compareTo=defaultCompareTo])

		Yields the minimum value. The minimum value is the value
		where ``compareTo(keySelector(value), currentMin)``
		returns -1 at the end.

	.. method:: sequenceEqual(other[, equals=defaultEquals])

		Yields True if both Observables yield the same values
		in the same order and complete.

	.. method:: singleAsync([predicate=truePredicate])

		Yields the first value where ``predicate(value) == True``
		or completes exceptionally with
		:class:`InvalidOperationException("No elements in observable") <rx.exceptions.InvalidOperationException>`
		if no value was found or with
		:class:`InvalidOperationException("More than one element in observable") <rx.exceptions.InvalidOperationException>`
		if more than one value was found.

	.. method:: singleAsyncOrDefault([predicate=truePredicate, default=None])

		Yields the first value where ``predicate(value) == True``,
		``default`` if no value was found or completes exceptionally with
		:class:`InvalidOperationException("More than one element in observable") <rx.exceptions.InvalidOperationException>`
		if more than one value was found.

	.. method:: sum([selector=identity])

		Yields the sum of ``selector(value)``.

	.. method:: toDictionary([keySelector=identity, elementSelector=identity])

		Yields a dict having every value inserted as
		``dict[keySelector(value)] = elementSelector(value)``.

		Completes exceptionally with :class:`Exception("Duplicate key: ...")`
		if multiple values have the same key.

	.. method:: toList()

		Yields a list containing all values.


Binding
-------

.. class:: Observable

	.. method:: multicast(subject)

		Returns a :class:`ConnectableObservable` that on
		:meth:`connect <ConnectableObservable.connect>` causes the current
		:class:`Observable` to push values into ``subject``.

	.. method:: multicastIndividual(subjectSelector, selector)

		Returns an :class:`Observable` sequence that contains the values of
		a sequence produced by multicasting the current :class:`Observable`
		within the ``selector`` function.

	.. method:: publish([initialValue=None])

		Equivalent to::

			if initialValue == None:
			    return self.multicast(Subject())
			else:
			    return self.multicast(BehaviorSubject(intialValue))

	.. method:: publishIndividual(selector[, initialValue=None])

		Equivalent to::

			if initialValue == None:
			    return self.multicastIndividual(lambda: Subject(), selector)
			else:
			    return self.multicastIndividual(lambda: BehaviorSubject(initialValue), selector)

	.. method:: publishLast([selector=None])

		Equivalent to::

			if selector == None:
			    return self.multicast(AsyncSubject())
			else:
			    return self.multicastIndividual(lambda: AsyncSubject(), selector)

	.. method:: refCount()

		Returns an :class:`Observable` sequence that stays connected
		to the current :class:`Observable` as long as there is at
		least one subscription to the :class:`Observable` sequence.

		.. note::

			Can only be used on a :class:`ConnectableObservable`.

	.. method:: replay([bufferSize=sys.maxsize, window=sys.maxsize, selector=None, scheduler=Scheduler.currentThread])

		If selector == None
			Returns a :class:`ConnectableObservable` that shares a single
			subscription to the current :class:`Observable` replaying ``bufferSize``
			notifications that are not older than ``window``.
		Else
			Returns an :class:`Observable` sequence that is the result of invoking
			``selector`` on a :class:`ConnectableObservable` that shares a
			single subscription to the current :class:`Observable` replaying
			``bufferSize`` notifications that are not older than ``window``.


Blocking
--------

.. class:: Observable

	.. method:: collect(getInitialCollector, merge[, getNewCollector=lambda _: getInitialCollector()])

		The initial accumulator is ``getInitialCollector()``.

		On every value ``accumulator = merge(accumulator, value)`` is called.

		Returns an iterable whos next value is the current accumulator which
		then gets replaced by ``getNowCollector(accumulator)``.

	.. method:: first([predicate=truePredicate])

		Returns the first value where ``predicate(value) == True``
		or completes exceptionally with
		:class:`InvalidOperationException("No elements in observable") <rx.exceptions.InvalidOperationException>`.

	.. method:: firstOrDefault([predicate=truePredicate, default=None])

		Returns the first value where ``predicate(value) == True`` or ``default``.

	.. method:: forEach(onNext)

		Calls ``onNext(value)`` for every value in the sequence. Blocks until
		the sequence ends.

	.. method:: forEachEnumerate(onNext)

		Calls ``onNext(value, index)`` for every value in the sequence. Blocks until
		the sequence ends.

	.. method:: getIterator()
				__iter__()

		Returns an iterator that yields all values of the sequence.

	.. method:: last([predicate=truePredicate])

		Returns the last value where ``predicate(value) == True``
		or completes exceptionally with
		:class:`InvalidOperationException("No elements in observable") <rx.exceptions.InvalidOperationException>`.

	.. method:: lastOrDefault([predicate=truePredicate, default=None])

		Returns the last value where ``predicate(value) == True`` or ``default``.

	.. method:: latest()

		Returns an iterator that blocks for the next values but in
		contrast to :meth:`getIterator` does not buffer values.

		Which means that the iterator returns the value that arrived
		latest but it will not return a value twice.

	.. method:: mostRecent(initialValue)

		Returns an iterator that returns values even if no new values
		have arrived. It is a sampling iterator.

		This means that the iterator can yield duplicates.

	.. method:: next()

		Returns an iterator that blocks until the next value arrives.

		If values arrive before the iterator moves to the next value,
		they will be dropped. :meth:`next` only starts waiting for the
		next value after the iterator requests for it.

	.. method:: singleAsync([predicate=truePredicate])

		Yields the first value where ``predicate(value) == True``
		or completes exceptionally with
		:class:`InvalidOperationException("No elements in observable") <rx.exceptions.InvalidOperationException>`
		if no value was found or with
		:class:`InvalidOperationException("More than one element in observable") <rx.exceptions.InvalidOperationException>`
		if more than one value was found.

	.. method:: singleAsyncOrDefault([predicate=truePredicate, default=None])

		Yields the first value where ``predicate(value) == True``,
		``default`` if no value was found or completes exceptionally with
		:class:`InvalidOperationException("More than one element in observable") <rx.exceptions.InvalidOperationException>`
		if more than one value was found.

	.. method:: wait()

		Is a synonym for :meth:`last`


Concurrent
----------

.. class:: Observable

	.. method:: subscribeOn(scheduler)

		Schedules subscriptions to the current :class:`Observable`
		immediately on ``scheduler``.

	.. method:: observeOn(scheduler)

		Whenever an onNext, onError, or onCompleted event happens, the
		invocation of the corresponding function on all observers is
		scheduled on ``scheduler``.

	.. method:: synchronize([gate=None])

		Whenever an onNext, onError, or onCompleted event happens, the
		invocation of the corresponding function on all observers is
		synchronized with ``gate``.

		If ``gate == None`` then ``gate = RLock()``.

		The synchronisation guarantees that only a single observer sees an
		onNext, onError, or onComplete call at the same time.


Creation
--------

.. class:: Observable

	.. staticmethod:: create(subscribe)

		Returns an :class:`Observable` that calls ``subscribe``
		every time an :class:`Observer <rx.observer.Observer>` subscribes.

		The observer will be passed as parameter to ``subscribe``.

		``subscribe`` should return a
		:class:`Disposable <rx.disposable.Disposable>`.

	.. staticmethod:: defer(observableFactory)

		Returns an :class:`Observable` that subscribes observers
		to the :class:`Observable` returned by ``observableFactory``.

		It calls ``observableFactory`` every time a subscription happens.

	.. staticmethod:: empty()

		Returns an :class:`Observable` that instantly completes
		on every subscription.

	.. staticmethod:: generate(initialState, condition, iterate, resultSelector[, scheduler=Scheduler.iteration])

		Returns an :class:`Observable` who represents the following generator::

			currentState = initialState

			while condition(currentState):
				yield resultSelector(currentState)
				currentState = iterate(currentState)

		The values are scheduled on ``scheduler``.

	.. staticmethod:: never()

		Returns an :class:`Observable` that has no values and never completes.

	.. staticmethod:: range(start, count[, scheduler=Scheduler.iteration])

		Returns an :class:`Observable` that yields ``count`` values beginning
		from ``start`` and then completes.

		The values are scheduled on ``scheduler``.

	.. staticmethod:: repeatValue(value[, count=None, scheduler=Scheduler.iteration])

		Returns an :class:`Observable` that yields ``value`` for ``count``
		times and then completes.

		If ``count == None`` ``value`` gets yielded indefinetly.

		The values are scheduled on ``scheduler``.

	.. staticmethod:: returnValue(value[, scheduler=Scheduler.constantTimeOperations])

		Returns an :class:`Observable` that yields ``value`` and then completes.

		The value is scheduled on ``scheduler``.

	.. staticmethod:: start(action[, scheduler=Scheduler.default])

		Returns an :class:`Observable` that yields the result of ``action()``
		scheduled for execution on ``scheduler``.

	.. staticmethod:: throw(exception[, scheduler=Scheduler.constantTimeOperations])

		Returns an :class:`Observable` that completes exceptionally with ``exception``.

		The exception is scheduled on ``scheduler``.

	.. staticmethod:: using(resourceFactory, observableFactory)

		Returns an :class:`Observable` that whenever an observer subscribes,
		calls ``resourceFactory()`` then ``observableFactory(resource)`` and
		subscribes the observer to the :class:`Observable` returned by
		``observableFactory``

		The resource returned by ``resourceFactory`` must have a ``dispose``
		method that is invoked once the :class:`Observable` returned by
		``observableFactory`` has completed.

	.. staticmethod:: fromFuture(future)

		Returns an :class:`Observable` that yields the value or exception
		of ``future``. If ``future`` is canceled the Observable completes
		exceptionally with Exception("Future was cancelled").

	.. staticmethod:: fromIterable(iterable[, scheduler=Scheduler.default])

		Returns an :class:`Observable` that yields all values from ``iterable``
		on ``scheduler``.

	.. staticmethod:: fromEvent(addHandler, removeHandler[, scheduler=Scheduler.default])

		Returns an :class:`Observable` that calls ``addHandler(onNext)``
		when the first :class:`Observer <rx.observer.Observer>` subscribes.
		Further subscriber share the same underlying handler.

		When the last subscriber unsubscribes, ``removeHandler(onNext)`` is called.


Imperative
----------

.. class:: Observable

	.. staticmethod:: case(selector, sources[, defaultSource=None])
					  case(selector, sources[, scheduler=Scheduler.constantTimeOperations])

		Subscribes :class:`Observer <rx.observer.Observer>` to
		``sources[selector()]``. If the key returned by ``selector()``
		is not found in ``sources`` then the observer is subscribed to
		``defaultSource``.

		If ``defaultSource == None`` then
		``defaultSource = Observable.empty(scheduler)``.

	.. staticmethod:: iterableFor(iterable, resultSelector)

		Concatenates the :class:`Observable` sequences obtained by running the
		``resultSelector`` for each element in the given ``iterable``.

	.. staticmethod:: branch(condition, thenSource[, elseSource=None])
					  branch(condition, thenSource[, scheduler=Scheduler.constantTimeOperations])

		Subscribes :class:`Observer <rx.observer.Observer>` to ``thenSource`` if
		``condition()`` returns ``True`` otherwise to ``elseSource``.

		If ``elseSource == None`` then
		``elseSource = Observable.empty(scheduler)``.

	.. method:: doWhile(condition, source)

		Repeats ``source`` as long as ``condition()`` returns ``True`` and at least once.
		``condition()`` is checked whenever ``source`` completes.

	.. method:: loop(condition, source)

		Repeats ``source`` as long as ``condition()`` returns ``True``.
		``condition()`` is checked whenever ``source`` completes.


Multiple
--------

.. class:: Observable

	.. method:: amb(*others)

		Subscribes :class:`Observer <rx.observer.Observer>` to the first
		:class:`Observable` that yields a value including ``self``.

	.. staticmethod:: amb(first, *others)

		See :meth:`amb`.

	.. method:: catchException(handler[, exceptionType=Exception])

		Continues an :class:`Observable` that is terminated by an exception
		that is an instance of ``exceptionType`` with the :class:`Observable` produced
		by ``handler(exception)``.

	.. method:: catchFallback(*sources)

		Continues an :class:`Observable` that is terminated by an exception
		with the next :class:`Observable`.

	.. method:: concat(*sources)

		Concatenates ``self`` with all ``sources``.

	.. staticmethod:: concat(*sources)

		See :meth:`concat`.

	.. method:: groupJoin(right, leftDurationSelector, rightDurationSelector, resultSelector)

		Whenever a value (``leftValue``) is yielded from the
		current :class:`Observable`, a new :class:`Observable`
		sequence is created. All previously arrived rightValues
		are replayed on the new Observable.

		Whenever a value (``rightValue``) is yielded from ``right``
		it is yielded on all :class:`Observable` sequences created from
		leftValues.

		Observables created from ``leftValue`` will complete after
		``leftDurationSelector(leftValue)`` yields the first value or
		completes normally.

		``rightValue`` values are remembered until
		``rightDurationSelector(rightValue)`` yields the first value or
		completes normally.

	.. method:: join(right, leftDurationSelector, rightDurationSelector, resultSelector)

		Whenever a value (``leftValue``) is yielded from the
		current :class:`Observable`,
		``resultSelector(leftValue, rightValue)`` is invoked for all
		previousely arrived values on ``right``.

		Whenever a value (``rightValue``) is yielded from ``right``,
		``resultSelector(leftValue, rightValue)`` is invoked for all
		previousely arrived values on the current :class:`Observable`.

		``leftValue`` values are remembered until
		``leftDurationSelector(leftValue)`` yields the first value or
		completes normally.

		``rightValue`` values are remembered until
		``rightDurationSelector(rightValue)`` yields the first value or
		completes normally.

	.. method:: merge([maxConcurrency=0])

		Merges all :class:`Observable` values in an :class:`Observable`.

		If ``maxConcurrency > 0`` then ``maxConcurrency`` events can happen
		at the same time.

	.. staticmethod:: onErrorResumeNext(*sources)

		Continues an :class:`Observable` that is terminated normally or by an
		exception with the next :class:`Observable`.

	.. method:: selectMany(onNextObservable[, onErrorObservable=None, onCompletedObservable=None])

		Merges ``onNextObservable``, ``onErrorObservable`` and
		``onCompletedObservable`` respectively whenever the corresponding
		event happens.

	.. method:: skipUntil(other)

		Skips values until ``other`` yields the first value or completes.

	.. method:: skipUntil(time[, scheduler=Scheduler.timeBasedOperation])

		Skips values until the timer created on ``scheduler`` completes
		after ``time``.

	.. method:: switch()

		Transforms an :class:`Observable` of :class:`Observable` values
		into an :class:`Observable` producing values only from the most
		recent :class:`Observable`.

	.. method:: takeUntil(other)

		Takes values until ``other`` yields the first value or completes.

	.. method:: takeUntil(time[, scheduler=Scheduler.timeBasedOperation])

		Takes values until the timer created on ``scheduler`` completes
		after ``time``.

	.. method:: zip(*others[, resultSelector=lambda *x: x])

		Merges all :class:`Observable` into one observable sequence by
		combining their elements in a pairwise fashion.

	.. staticmethod:: zip(*sources[, resultSelector=lambda *x: x])

		See :meth:`zip`


Single
------

.. class:: Observable

	.. method:: asObservable()

		Hides the original type of the :class:`Observable`.

	.. method:: buffer(count[, skip=count])

		Buffers ``count`` values and yields them as list. Creates
		a new buffer every ``skip`` values.

	.. method:: defaultIfEmpty([default=None])

		Yields ``default`` if the current :class:`Observable` is empty.

	.. method:: dematerialize()

		Turns an :class:`Observable` of
		:class:`Notification <rx.notification.Notification>` values
		into and :class:`Observable` representing this notifications.

	.. method:: distinct([keySelector=identity])

		Yields distinct values of the current :class:`Observable`::

			1 1 2 1 3 -> 1 2 3

	.. method:: distinctUntilChanged([keySelector=identity, equals=defaultEquals])

		Yields distinct values of the current :class:`Observable` until the value changes::

			1 1 2 1 3 -> 1 2 1 3

	.. method:: do([onNext=noop, onError=noop, onCompleted=noop])

		Invoke ``onNext`` on each value, ``onError`` on exception and
		``onComplete`` on completion of the :class:`Observable`.

	.. method:: doFinally(action)

		Invokes ``action`` if the :class:`Observable` completes normally
		or exceptionally.

	.. method:: groupBy([keySelector=identity, elementSelector=identity])

		Yields :class:`GroupedObservable` sequences that yield
		``elementSelector(value)`` for all values where
		``keySelector(value)`` matches their :attr:`key <GroupedObservable.key>`.

	.. method:: groupByUntil(keySelector, elementSelector, durationSelector)

		Yields :class:`GroupedObservable` sequences that yield
		``elementSelector(value)`` for all values where
		``keySelector(value)`` matches their :attr:`key <GroupedObservable.key>`.

		Every :class:`GroupedObservable` completes when the :class:`Observable`
		returned by ``durationSelector(key)`` yields the first value or
		completes normally.

	.. method:: ignoreElements()

		Ignores all values from the original :class:`Observable`.

	.. method:: materialize()

		Turns values, exception and completion into
		:class:`Notification <rx.notification.Notification>` values.
		Completes when the original :class:`Observable` completes normally or
		exceptionally.

	.. method:: ofType(tpe)

		Yields all values from the current :class:`Observable` where
		``isinstance(value, tpe) == True``.

	.. method:: repeatSelf([count=indefinite])

		Repeats the original :class:`Observable` ``count`` times.

	.. method:: retry([count=indefinite])

		Retries the original :class:`Observable` ``count`` times until
		it does not complete exceptionally.

	.. method:: scan([seed=None, accumulator=None])

		Applies ``result = accumulator(result, value)`` over the values of the :class:`Observable`
		and yields each intermediate result

	.. method:: select(selector)

		Yields ``selector(value)`` for all values in the current
		:class:`Observable`.

	.. method:: selectEnumerate(selector)

		Yields ``selector(value, index)`` for all values in the
		current :class:`Observable`.

	.. method:: selectMany(onNext[, onError=None, onCompleted=None])

		Merges the :class:`Observable` sequence returned by
		``onNext(value)``, ``onError(exception)`` and ``onCompleted()``.

	.. method:: selectManyEnumerate(onNext[, onError=None, onCompleted=None])

		Merges the :class:`Observable` sequence returned by
		``onNext(value, index)``, ``onError(exception, index)``
		and ``onCompleted()``.
	.. method:: skip(count)

		Skips ``count`` values.

	.. method:: skipWhile(predicate)

		Skips values while ``predicate(value) == True``.

	.. method:: skipWhileEnumerate(predicate)

		Skips values while ``predicate(value, index) == True``.

	.. method:: skipLast(count)

		Skips the last ``count`` values.

	.. method:: startWith(*values)

		Prepends ``values`` to the :class:`Observable`.

	.. method:: take(count)

		Takes ``count`` values.

	.. method:: takeWhile(predicate)

		Takes values while ``predicate(value) == True``.

	.. method:: takeWhileEnumerate(predicate)

		Takes values while ``predicate(value, index) == True``.

	.. method:: takeLast(count)

		Takes the last ``count`` values.

	.. method:: takeLastBuffer(count)

		Takes the last ``count`` values and yields them as list.

	.. method:: where(predicate)

		Yields only values where ``predicate(value) == True``.

	.. method:: whereEnumerate(predicate)

		Yields only values where ``predicate(value, index) == True``.

	.. method:: window(count[, skip=count])

		Yields an :class:`Observable` every ``skip`` values that yields
		it self the next ``count`` values.


Time
----

.. class:: Observable

	.. method:: bufferWithTime(timeSpan[, timeShift=timeSpan, scheduler=Scheduler.timeBasedOperation])

		Buffers values for ``timeSpan``.
		Creates a new buffer every ``timeShift``.
		Uses ``scheduler`` to create timers.

	.. method:: bufferWithTimeAndCount(timeSpan, count[, scheduler=Scheduler.timeBasedOperation])

		Buffers values for ``timeSpan`` or until ``count`` many arrived.
		Uses ``scheduler`` to create timers.

	.. method:: delayRelative(dueTime[, scheduler=Scheduler.timeBasedOperation])

		Delays all values and normal completion for ``dueTime``.
		All events are scheduled on ``scheduler``.

	.. method:: delayAbsolute(dueTime[, scheduler=Scheduler.timeBasedOperation])

		Delays an :class:`Observable` until ``dueTime``.
		The time from now until dueTime is recorded and all values and
		normal completion is delayed as in :meth:`delayRelative`.
		All events are scheduled on ``scheduler``.

	.. method:: delayIndividual(delayDurationSelector[, subscriptionDelayObservable=None])

		Delays subscription until ``subscriptionDelayObservable`` yields
		the first value or completes normally.

		If ``subscriptionDelayObservable == None``
		subscription happens immediately.

		All values are delayed until the :class:`Observable` returned
		by ``delayDurationSelector(value)`` yields the first value
		or completes normally.

	.. method:: delaySubscriptionRelative(dueTime[, scheduler=Scheduler.timeBasedOperation])

		Delays subscription to the current observable for ``dueTime`` and
		schedules it on ``scheduler``.

	.. method:: delaySubscriptionAbsolute(dueTime[, scheduler=Scheduler.timeBasedOperation])

		Delays subscription to the current observable to ``dueTime`` and
		schedules it on ``scheduler``.

	.. staticmethod:: generateRelative(initialState, condition, iterate, resultSelector, timeSelector[, scheduler=Scheduler.timeBasedOperation])

		Returns an :class:`Observable` who represents the following generator::

			currentState = initialState

			while condition(currentState):
				yield resultSelector(currentState)
				currentState = iterate(currentState)

		but whose values are delayed for ``timeSelector(value)`` time.

	.. staticmethod:: generateAbsolute(initialState, condition, iterate, resultSelector, timeSelector[, scheduler=Scheduler.timeBasedOperation])

		Returns an :class:`Observable` who represents the following generator::

			currentState = initialState

			while condition(currentState):
				yield resultSelector(currentState)
				currentState = iterate(currentState)

		but whose values are delayed to time ``timeSelector(value)``.

	.. staticmethod:: interval(period[, scheduler=Scheduler.timeBasedOperation])

		Returns an :class:`Observable` sequence that yields an increasing
		index every ``period``.

		Values are scheduled on ``scheduler``.

	.. method:: sampleWithTime(interval[, scheduler=Scheduler.timeBasedOperation])

		Yields the latest value every ``interval``. Can yield duplicates.

		Uses ``scheduler`` to create timers.

	.. method:: sampleWithObservable(sampler)

		Yields the latest value whenever ``sampler`` yields a value.

	.. method:: skipWithTime(time[, scheduler=Scheduler.timeBasedOperation])

		Skips values for ``time``. ``scheduler`` is required to create a timer.

	.. method:: skipLastWithTime(time[, scheduler=Scheduler.timeBasedOperation])

		Skips values starting ``time`` before the :class:`Observable` completes.
		Values are yielded on ``scheduler``.

	.. method:: takeWithTime(time[, scheduler=Scheduler.timeBasedOperation])

		Takes values for ``time``. ``scheduler`` is required to create a timer.

	.. method:: takeLastWithTime(time[, scheduler=Scheduler.timeBasedOperation])

		Takes values starting ``time`` before the :class:`Observable` completes.
		Values are yielded on ``scheduler``.

	.. method:: takeLastBufferWithTime(time[, scheduler=Scheduler.timeBasedOperation])

		Takes values starting ``time`` before the :class:`Observable` completes
		and yields them as list

	.. method:: throttle(dueTime[, scheduler=Scheduler.timeBasedOperation])

		Ignores values which are followed by another value
		before ``dueTime`` elapsed.

	.. method:: throttleIndividual(durationSelector)

		Ignores values which are followed by another value
		before the :class:`Observable` returned by ``durationSelector(value)``
		yields the first value or completes normally.

	.. method:: timeInterval([scheduler=Scheduler.timeBasedOperation])

		Yields { value = value, interval = scheduler.now() - lastArrivalTime }

	.. method:: timeoutRelative(dueTime[\
								, other=Observable.throw(Exception("Timeout in observable"))\
								, scheduler=Scheduler.timeBasedOperation])

		Returns the current :class:`Observable` sequence or ``other``
		if the current :class:`Observable` sequence
		did not yield any value nor complete until ``dueTime`` elapsed.

	.. method:: timeoutAbsolute(dueTime[\
								, other=Observable.throw(Exception("Timeout in observable"))\
								, scheduler=Scheduler.timeBasedOperation])

		Returns the current :class:`Observable` sequence or ``other``
		if the current :class:`Observable` sequence
		did not yield any value nor complete until ``dueTime``.

	.. method:: timeoutIndividual(durationSelector[,\
								  firstTimeout=Observable.never(),\
								  other=Observable.throw(Exception("Timeout in observable")))

		Applies a timeout policy to the observable sequence based on an initial
		timeout duration for the first element, and a timeout duration computed
		for each subsequent element.

		If the next element isn't received within the computed duration
		starting from its predecessor, the other observable sequence is used
		to produce future messages from that point on.

	.. staticmethod:: timerRelative(dueTime[, period=None, scheduler=Scheduler.timeBasedOperation])

		Creates an :class:`Observable` sequence that yields ``0`` after
		``dueTime`` and the completes.

		If ``period != None`` then the :class:`Observable` does not complete
		but yield ``1, 2, ...`` every ``period``.

	.. staticmethod:: timerAbsolute(dueTime[, period=None, scheduler=Scheduler.timeBasedOperation])

		Creates an :class:`Observable` sequence that yields ``0`` at
		``dueTime`` and the completes.

		If ``period != None`` then the :class:`Observable` does not complete
		but yield ``1, 2, ...`` every ``period``.

	.. method:: timestamp([scheduler=Scheduler.timeBasedOperation])

		Yields { value = value, timestamp = scheduler.now() }

	.. method:: windowWithTime(timeSpan[, timeShift=timeSpan, scheduler=Scheduler.timeBasedOperation])

		Yields an :class:`Observable` every ``timeShift`` that yields
		it self the next values for ``timeSpan``.

	.. method:: windowWithTimeAndCount(timeSpan, count[, scheduler=Scheduler.timeBasedOperation])

		Yields :class:`Observable` values that yield the values from the
		current :class:`Observable` for ``timeSpan`` or until ``count`` number
		of values have arrived.








