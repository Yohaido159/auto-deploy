subscribers = dict()


async def subscribe(event_type: str, fn) -> None:
    if not event_type in subscribers:
        subscribers[event_type] = list()

    subscribers[event_type].append(fn)


def post_event(event_type: str, *args, **kwargs):
    if not event_type in subscribers:
        return
    for fn in subscribers[event_type]:
        fn(*args, **kwargs)
