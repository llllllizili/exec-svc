from datetime import datetime


class SmartError:
    def __init__(self, error, start_date, target):
        self.error = error
        self.start_date = start_date
        self.end_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.target = target

    def reply(self):
        return dict(start_date=self.start_date, status='FAILURE', target=self.target,
                        result=self.error, end_date=self.end_date)








