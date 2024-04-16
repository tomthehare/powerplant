import json
import os.path

from models.water_queue_entry import WaterQueueEntry

FILE_LOCATION_DEFAULT = "watering-queue.json"

class WaterQueueClient:

    def get_water_queue_file_location(self) -> str:
        return FILE_LOCATION_DEFAULT

    def get_queue(self) -> list[WaterQueueEntry]:
        return_list = []

        with open(self.get_water_queue_file_location(), 'r') as f:
            queue = json.load(f)

        for q in queue:
            return_list.append(WaterQueueEntry.parse_obj(q))

        return return_list

    def _save_queue(self, queue: list[WaterQueueEntry]):
        with open(self.get_water_queue_file_location(), 'w') as f:
            f.write(json.dumps([a.dict() for a in queue], indent=2))

    def enqueue_entry(self, entry: WaterQueueEntry):
        queue = self.get_queue()
        queue.insert(0, entry)

        self._save_queue(queue)

    def dequeue_entry(self):
        queue = self.get_queue()

        if len(queue) > 0:
            queue.pop()
            self._save_queue(queue)

    def ensure_water_queue_exists(self):
        if not os.path.exists(self.get_water_queue_file_location()):
            with open(self.get_water_queue_file_location(), 'w') as f:
                f.write("[]")
