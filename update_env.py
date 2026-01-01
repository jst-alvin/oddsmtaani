#!/usr/bin/env python
"""Update .env file with new credentials."""

new_consumer_key = "iYJkZXx3EZqZQDhd6i9wfGRgsp6W88P8AUrY9wsaKTXAEUpV"
new_consumer_secret = "iYJkZXx3EZqZQDhd6i9wfGRgsp6W88P8AUrY9wsaKTXAEUpV"

with open('.env', 'r') as f:
    lines = f.readlines()

updated_lines = []
for line in lines:
    if line.startswith('MPESA_CONSUMER_KEY='):
        updated_lines.append(f'MPESA_CONSUMER_KEY={new_consumer_key}\n')
    elif line.startswith('MPESA_CONSUMER_SECRET='):
        updated_lines.append(f'MPESA_CONSUMER_SECRET={new_consumer_secret}\n')
    else:
        updated_lines.append(line)

with open('.env', 'w') as f:
    f.writelines(updated_lines)

print('✅ .env file updated with new credentials')
