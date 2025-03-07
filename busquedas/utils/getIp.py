def obtener_ip(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip:
        ip = ip.split(',')[0]  # Si hay múltiples IPs, toma la primera
    else:
        ip = request.META.get('REMOTE_ADDR')  # Alternativa si no existe HTTP_X_FORWARDED_FOR
    return ip
 