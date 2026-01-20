from prometheus_client import start_http_server, Summary
import random
import time

# By default counters, histograms, and summaries export an additional series suffixed with _created and a value of the unix timestamp for when the metric was created. 
# If this information is not helpful, it can be disabled by setting the environment variable PROMETHEUS_DISABLE_CREATED_SERIES=True or in code:

from prometheus_client import disable_created_metrics
disable_created_metrics()

# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_time', 'Time spent processing request')

from prometheus_client import Counter, Gauge
c = Counter('func_call_counter', 'number of times the function is called.')
g = Gauge('wait_time_gauge', 'the wait time input to the function')

# Decorate function with metric.
@REQUEST_TIME.time()
def process_request(t):
    """A dummy function that takes some time."""
    # sleep for the supplied delay seconds
    time.sleep(t)
    # increment the usage counter
    c.inc()
    # add the delay time to the accumulator
    g.set(t)

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(18000)
    # Generate some requests.
    while True:
        # create a random delay
        delay_in_seconds = int(10*random.random())
        # process the request with that random delay
        process_request(delay_in_seconds)
        
