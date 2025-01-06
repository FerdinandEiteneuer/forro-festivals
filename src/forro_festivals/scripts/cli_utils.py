import click


def parse_event_ids_range(s):
    """Regular expression to match numbers and ranges (e.g., '11, 12, 13-15, 19')"""
    result = []
    for part in s.replace(' ', '').split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            result.extend(range(start, end + 1))
        else:
            result.append(int(part))
    return result

def validate_event_ids(ctx, param, value):
    """Callback function for """
    try:
        event_ids = parse_event_ids_range(value)
        if not all(isinstance(event_id, int) for event_id in event_ids):
            raise ValueError('Bad Input')
        return event_ids
    except Exception as e:
        raise click.BadParameter(f"Invalid event ID format {e}. Value: {value}. Expected format like: '1,3-5,10,19-29'.")

