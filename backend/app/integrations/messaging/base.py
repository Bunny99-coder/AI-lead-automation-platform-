from abc import ABC, abstractmethod


class SmsProvider(ABC):
    @abstractmethod
    async def send_sms(self, phone: str, message: str) -> dict: ...


class EmailProvider(ABC):
    @abstractmethod
    async def send_email(self, email: str, subject: str, body: str) -> dict: ...
