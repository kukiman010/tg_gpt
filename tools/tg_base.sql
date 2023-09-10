-- SET statement_timeout = 0;
-- SET client_encoding = 'UTF8';
-- SET standard_conforming_strings = on;
-- SET check_function_bodies = false;
-- SET client_min_messages = warning;


CREATE TABLE users (
    user_id BIGINT UNIQUE,
    login TEXT UNIQUE,
    status BIGINT,
    type TEXT,
    id BIGSERIAL PRIMARY KEY
);

CREATE TABLE users_in_groups (
    user_id BIGINT UNIQUE,
    chats_id BIGINT[],
    id BIGSERIAL PRIMARY KEY
);

CREATE TABLE context (
    user_id BIGINT,
    chat_id BIGINT,
    role    TEXT,
    message_id BIGINT,
    message TEXT,
    id BIGSERIAL PRIMARY KEY
);

CREATE TABLE admins (
    user_id BIGINT UNIQUE,
    login TEXT UNIQUE,
    status BIGINT,
    id BIGSERIAL PRIMARY KEY
);




-- CREATE TABLE statistic (
--     id BIGSERIAL PRIMARY KEY
-- );


CREATE TABLE model_gpt (
    model TEXT,
    description TEXT,
    id BIGSERIAL PRIMARY KEY
);


CREATE TABLE voices(
    name TEXT,
    language TEXT,
    gender TEXT,
    language_code TEXT,
    id BIGSERIAL PRIMARY KEY
);

-- CREATE TABLE user_settings(
--     user_id BIGINT,

-- );




-- DROP FUNCTION add_chats_id(p_user_id BIGINT, p_chats_id BIGINT[]) 
CREATE FUNCTION add_chats_id(p_user_id BIGINT, p_chats_id BIGINT[]) 
RETURNS VOID AS $$
BEGIN
    -- Проверяем наличие записи с заданным user_id
    IF EXISTS (SELECT 1 FROM users_in_groups WHERE user_id = p_user_id) THEN
        -- Если запись существует, добавляем только уникальные значения в массив chats_id
        UPDATE users_in_groups SET chats_id = ARRAY(SELECT DISTINCT unnest(chats_id) UNION SELECT unnest(p_chats_id))
        WHERE user_id = p_user_id;
    ELSE
        -- Если записи не существует, создаем новую запись и указываем chats_id
        INSERT INTO users_in_groups (user_id, chats_id) VALUES (p_user_id, p_chats_id);
    END IF;
END;
$$ LANGUAGE plpgsql;



-- DROP FUNCTION get_chats_id(IN p_user_id BIGINT)
CREATE OR REPLACE FUNCTION get_chats_id(IN p_user_id BIGINT)
    RETURNS SETOF BIGINT[] AS
$$
BEGIN
    RETURN QUERY 
    SELECT chats_id 
    FROM users_in_groups 
    WHERE users_in_groups.user_id = p_user_id;
END;
$$
LANGUAGE plpgsql;





-- -- https://platform.openai.com/docs/models/continuous-model-upgrades
-- -- gpt-4-32k-0314
-- -- text-davinci-002
-- -- text-babbage-001

-- insert into model_gpt values('gpt-3.5-turbo', 'default');
-- insert into model_gpt values('gpt-4', '');
-- insert into model_gpt values('gpt-4-32k-0314', 'actual(no supported)');
-- -- insert into model_gpt values('', '');


-- -- https://cloud.yandex.com/en-ru/docs/speechkit/tts/voices
-- insert into voices values('dasha',  'Russian',  'F','ru-RU');
-- insert into voices values('alena',  'Russian',  'F','ru-RU');
-- insert into voices values('lea',    'German',   'F','de-DE');
-- insert into voices values('john',   'English',  'M','en-US');
-- insert into voices values('naomi',  'Hebrew',   'F','he-IL');
-- insert into voices values('amira',  'Kazakh',   'F','kk-KK');
-- insert into voices values('madi',   'Kazakh',   'M','kk-KK');
-- insert into voices values('nigora', 'Uzbek',    'F','uz-UZ');
-- -- insert into voices values('','','','');