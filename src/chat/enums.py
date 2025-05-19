from enumfields import Enum

class ChatMessageType(Enum):
    TEXT = 'Text'
    COUNTER_OFFER = 'Counter Offer'

class ChatRoomStatus(Enum):
    ACTIVE = 'active'
    IN_PROGRESS = 'in progress'
    PENDING = 'pending'
    COMPLETED = 'completed'
