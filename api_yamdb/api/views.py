from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api import const
from api.serializers import SignUpSerializer, TokenAccessObtainSerializer
from api.utils import send_confirmation_code
from reviews.models import User
from users.models import ConfirmationCode


class SignUpAPIView(APIView):
    """Обрабатывает POST запрос на регистрацию нового пользователя."""

    def post(self, request):
        data = request.data
        serializer = SignUpSerializer(data=data)
        user = User.objects.filter(
            username=data.get('username'), email=data.get('email')
        ).first()

        if user:
            diff_time = (
                timezone.now() - user.confirmation_code.created_at
            ).seconds
            if diff_time < const.TIMEOUT:
                return Response(
                    {
                        'message': f'Повторная отправка кода возможна '
                        f'через {60 - diff_time} секунд.'
                    },
                    status=status.HTTP_200_OK,
                )
            user.confirmation_code.code = get_random_string(const.CODE_LENGTH)
            user.confirmation_code.save()
            send_confirmation_code(user.confirmation_code, user.email)
            return Response(
                {'message': 'Код отправлен на ваш email'},
                status=status.HTTP_200_OK,
            )

        if serializer.is_valid():
            instance = serializer.save()
            confirmation_code = ConfirmationCode.objects.create(
                user=instance, code=get_random_string(const.CODE_LENGTH)
            )
            send_confirmation_code(confirmation_code, instance.email)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenAccessObtainView(APIView):
    """Обрабатывает POST запрос на получения токена."""

    def post(self, request):
        serializer = TokenAccessObtainSerializer(
            data=request.data, context=request.data
        )
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            if not user.is_active:
                user.is_active = True
                user.save()

            return Response(
                {'token': str(refresh.access_token)}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
