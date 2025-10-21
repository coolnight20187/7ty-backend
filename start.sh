#!/bin/bash
echo "Dang xay dung va khoi chay cac container Docker..."
echo "(Qua trinh nay co the mat vai phut o lan dau tien)"
echo ""

# Chay docker-compose
docker-compose up --build

echo ""
echo "========================================="
echo " HE THONG DA DUNG LAI"
echo "========================================="
echo "Nhan phim bat ky de dong cua so nay."
read -p "Press any key to continue . . ."