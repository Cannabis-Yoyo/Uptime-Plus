import requests
import logging
import time


class WebsiteMonitor:
    def __init__(self, sites, failure_threshold=3):
        self.sites = sites
        self.failure_threshold = failure_threshold
        self.state = {}

        for site in self.sites:
            self.state[site["url"]] = {
                "fail_count": 0,
                "alert_sent": False
            }

    def check_website(self, url, timeout=10):
        try:
            start = time.time()
            response = requests.get(url, timeout=timeout)
            response_time = round(time.time() - start, 3)

            return {
                "status": "UP" if response.status_code == 200 else "ERROR",
                "status_code": response.status_code,
                "response_time": response_time,
                "error": None
            }

        except requests.exceptions.RequestException as e:
            return {
                "status": "DOWN",
                "status_code": None,
                "response_time": None,
                "error": str(e)
            }

    def run_check(self):
        results = []

        for site in self.sites:
            url = site["url"]
            max_time = site["max_response_time"]
            result = self.check_website(url)

            state = self.state[url]

            issue = (
                result["status"] != "UP"
                or (result["response_time"] and result["response_time"] > max_time)
            )

            if issue:
                state["fail_count"] += 1
            else:
                state["fail_count"] = 0
                state["alert_sent"] = False

            results.append({
                "url": url,
                "status": result["status"],
                "response_time": result["response_time"],
                "fail_count": state["fail_count"],
                "alert_ready": state["fail_count"] >= self.failure_threshold and not state["alert_sent"]
            })

        return results
