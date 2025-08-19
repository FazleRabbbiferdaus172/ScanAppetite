from io import BytesIO
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect

from orders.models import OrderItem


@login_required
def view_item_barcode(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)
    # Security check
    if request.user != item.order.customer and request.user != item.meal.vendor:
        return HttpResponse("Unauthorized", status=403)

    try:
        import qrcode
        import qrcode.image.svg

        # Create a QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        # Add the item's unique barcode_id as the data
        qr.add_data(str(item.barcode_id))
        qr.make(fit=True)

        # Create an SVG image from the QR Code instance
        img = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)

        # Write to a buffer
        buffer = BytesIO()
        img.save(buffer)
        buffer.seek(0)

        return HttpResponse(buffer.getvalue(), content_type='image/svg+xml')

    except ImportError:
        # Fallback or error message if qrcode library is missing
        return HttpResponse("QR Code generation library is not installed.", status=500)


@login_required
def printable_barcode_view(request, item_id):
    # Security: Ensure user is a vendor and this item belongs to them
    item = get_object_or_404(OrderItem, id=item_id, meal__vendor=request.user)
    return render(request, 'orders/printable_barcode.html', {'item': item})


@login_required
def print_bulk_barcodes_view(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids')

        # Security: Fetch only items that belong to the logged-in vendor
        items = OrderItem.objects.filter(
            id__in=item_ids,
            meal__vendor=request.user,
            status=OrderItem.FulfillmentStatus.READY_FOR_PICKUP
        )

        return render(request, 'orders/printable_bulk_barcodes.html', {'items': items})

    return redirect('vendor_dashboard')


@login_required
def qr_code_scanner_view(request):
    # This view just renders the scanner template
    return render(request, 'orders/qr_code_scanner.html')


@login_required
def scan_and_verify_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            barcode_id = data.get('barcode_id')

            # Find the order item with this barcode ID, ensuring it belongs to the current user
            item = OrderItem.objects.get(
                barcode_id=barcode_id,
                order__customer=request.user,
                status=OrderItem.FulfillmentStatus.READY_FOR_PICKUP
            )

            # If found, update the status
            item.status = OrderItem.FulfillmentStatus.DELIVERED
            item.save()

            return JsonResponse({'success': True, 'message': f"Pickup confirmed for '{item.meal.name}'!"})

        except OrderItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid or incorrect barcode scanned.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'An unexpected error occurred.'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)
