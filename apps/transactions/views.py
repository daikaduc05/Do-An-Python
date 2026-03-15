from django.db import transaction as db_transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Transaction, OwnedEbook
from apps.accounts.models import User
from apps.ebooks.models import Ebook


class DepositView(APIView):
    """Nạp tiền vào tài khoản"""

    def post(self, request):
        amount = request.data.get('amount', 0)
        user_id = request.data.get('user_id')

        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return Response({'error': 'Số tiền không hợp lệ'}, status=400)

        if amount <= 0:
            return Response({'error': 'Số tiền không hợp lệ'}, status=400)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User không tồn tại'}, status=404)

        user.deposit(amount)

        Transaction.objects.create(
            user=user,
            type='deposit',
            amount=amount,
            description=f'Nạp {amount} Coins',
            balance_after=user.balance
        )

        return Response({
            'message': f'Nạp thành công {amount} Coins',
            'new_balance': user.balance
        })


class PurchaseEbookView(APIView):
    permission_classes = [IsAuthenticated]

    @db_transaction.atomic
    def post(self, request):
        ebook_id = request.data.get('ebook_id')
        user = User.objects.select_for_update().get(pk=request.user.pk)

        if not ebook_id:
            return Response({'error': 'Thiếu ebook_id'}, status=400)

        try:
            ebook = Ebook.objects.get(id=ebook_id, is_active=True)
        except Ebook.DoesNotExist:
            return Response({'error': 'Sách không tồn tại'}, status=404)

        already_owned = OwnedEbook.objects.filter(user=user, ebook=ebook).exists()
        if already_owned:
            return Response({'error': 'Bạn đã mua sách này rồi'}, status=400)

        if not user.can_purchase(ebook.price):
            return Response({
                'error': 'Bạn không đủ xu để mua sách này',
                'current_balance': user.balance,
                'ebook_price': ebook.price
            }, status=400)

        user.purchase(ebook.price)

        tx = Transaction.objects.create(
            user=user,
            type='purchase',
            amount=-ebook.price,
            ebook=ebook,
            description=f"Mua ebook: {ebook.title}",
            balance_after=user.balance
        )

        OwnedEbook.objects.create(
            user=user,
            ebook=ebook,
            transaction=tx,
            purchased_price=ebook.price
        )

        return Response({
            'message': 'Mua sách thành công',
            'balance_after': user.balance,
            'ebook': {
                'id': ebook.id,
                'title': ebook.title,
                'price': ebook.price,
            }
        }, status=201)


class MyLibraryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        owned = (
            OwnedEbook.objects
            .filter(user=request.user)
            .select_related('ebook', 'ebook__author', 'ebook__category')
            .order_by('-purchased_at')
        )

        data = []
        for item in owned:
            ebook = item.ebook
            data.append({
                'ownership_id': item.id,
                'purchased_at': item.purchased_at.isoformat(),
                'purchased_price': item.purchased_price,
                'ebook': {
                    'id': ebook.id,
                    'title': ebook.title,
                    'author': ebook.author.name,
                    'category': ebook.category.name if ebook.category else 'Chưa phân loại',
                    'price': ebook.price,
                    'cover': ebook.cover_url,
                    'file_url': ebook.file_url,
                    'file_mime': ebook.file_mime,
                }
            })

        return Response({'library': data})


class TransactionListView(APIView):
    """Lịch sử giao dịch"""

    def get(self, request):
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({'error': 'User ID required'}, status=400)

        transactions = Transaction.objects.filter(user_id=user_id)[:50]

        data = [{
            'id': t.id,
            'type': t.get_type_display(),
            'amount': t.amount,
            'description': t.description,
            'balance_after': t.balance_after,
            'created_at': t.created_at.isoformat(),
        } for t in transactions]

        return Response({'transactions': data})