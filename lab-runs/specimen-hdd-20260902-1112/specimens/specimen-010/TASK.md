# TASK

Process inherits `KEY=/x`. A dotenv-style file contains `KEY=`. After load, some tools still see `/x`, some see empty, some fall back to a default. The developer wants to know which layer treated empty as “unset” and which value actually won.
