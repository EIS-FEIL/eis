-- Loome uue rolli (grupi)
CREATE ROLE eisikud;

-- Anname õigused

\c eisdb1;
GRANT ALL PRIVILEGES ON SCHEMA public TO eisikud;
GRANT ALL PRIVILEGES ON SCHEMA plank TO eisikud;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO eisikud;
GRANT SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO eisikud;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO eisikud;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA plank TO eisikud;
GRANT SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA plank TO eisikud;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA plank TO eisikud;

\c eisdb1sess;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO eisikud;
GRANT SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO eisikud;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO eisikud;

\c eisdb1log;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO eisikud;
GRANT SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO eisikud;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO eisikud;

-- Loome rakenduse kasutajad
CREATE ROLE eisik11 WITH login password 'eisik';  
CREATE ROLE eisik12 WITH login password 'eisik';  
CREATE ROLE eisik13 WITH login password 'eisik';
CREATE ROLE eisik21 WITH login password 'eisik';
CREATE ROLE eisik22 WITH login password 'eisik';
CREATE ROLE eisik23 WITH login password 'eisik';

-- Lisame gruppidesse
GRANT eisikud to eisik11;
GRANT eisikud to eisik12;
GRANT eisikud to eisik13;

GRANT eisikud to eisik21;
GRANT eisikud to eisik22;
GRANT eisikud to eisik23;
