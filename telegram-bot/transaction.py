import uuid
import datetime

class Transaction:

    def __init__(self):
        self.uuid = uuid.uuid4()

    def _parse_dttm_from_msg(self, msg):
        # TBD
        return None

    def parse_from_message(self, msg):
        parsed = msg.split(sep = ' ')
        self.amount_lcy = parsed[0]
        self.currency_code = parsed[1]
        self.place = parsed[2]
        if len(parsed) == 4:
            self.lcl_dttm = self._parse_dttm_from_msg()
        else:
            self.lcl_dttm = int(datetime.datetime.now().timestamp())


if __name__ == '__main__':
    x = Transaction()
    print(x.uuid)

    y = Transaction()
    print(y.uuid)