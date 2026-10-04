# Week 3 Activity Notes

## Observation 1

The middleware counts every request path, including `/metrics` itself.

## Observation 2

The `/metrics` response provides both per-endpoint request counts and the total request count, showing which endpoints were used and how many requests the service handled.
