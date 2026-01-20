from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Transaction
from apps.accounts.models import User


class DepositView(APIView):
    """Nạp tiền vào tài khoản"""
    
    def post(self, request):
        amount = request.data.get('amount', 0)
        user_id = request.data.get('user_id')
        
        if amount <= 0:
            return Response({'error': 'Số tiền không hợp lệ'}, status=400)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User không tồn tại'}, status=404)
        
        # Cộng tiền vào tài khoản
        user.deposit(amount)
        
        # Tạo giao dịch
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
