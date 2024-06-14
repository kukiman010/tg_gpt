-- SET statement_timeout = 0;
-- SET client_encoding = 'UTF8';
-- SET standard_conforming_strings = on;
-- SET check_function_bodies = false;
-- SET client_min_messages = warning;
SET client_encoding = 'UTF8';


CREATE TABLE users (
    user_id             BIGINT UNIQUE,
    login               TEXT UNIQUE,
    status_user         BIGINT,
    wait_action         TEXT,
    type                TEXT,
    company_ai          TEXT,
    model               TEXT,
    speaker_name        TEXT,
    language_code       TEXT,
    model_rec_photo     TEXT,
    model_gen_pthoto    TEXT,
    text_to_audio       TEXT,
    audio_to_text       TEXT,
    last_login          TIMESTAMP,
    registration_date   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id                  BIGSERIAL PRIMARY KEY
);


CREATE TABLE users_in_groups (
    user_id             BIGINT UNIQUE,
    chats_id            BIGINT[],
    id                  BIGSERIAL PRIMARY KEY
);

CREATE TABLE default_data (
    user_id             TEXT UNIQUE,
    chats_id            TEXT
);

-- TODO: add column data , тип записи сообщения
CREATE TABLE context (
    user_id             BIGINT,
    chat_id             BIGINT,
    role                TEXT,
    message_id          BIGINT,
    message             TEXT,
    isPhoto             BOOLEAN,
    id                  BIGSERIAL PRIMARY KEY
);

CREATE TABLE prompt (
    user_id             BIGINT,
    prompt              TEXT,
    id                  BIGSERIAL PRIMARY KEY
);


CREATE TABLE admins (
    user_id             BIGINT UNIQUE,
    login               TEXT UNIQUE,
    status              BIGINT,
    id                  BIGSERIAL PRIMARY KEY
);


CREATE TABLE assistant_ai (
    company_ai          TEXT,
    model_name          TEXT,
    description         TEXT,
    token_size          INT,
    last_update         TEXT,
    status_lvl          BIGINT,
    isView              BOOLEAN,
    id                  BIGSERIAL PRIMARY KEY
);

CREATE TABLE assistant_ai_photo (
    company_ai          TEXT,
    model_name          TEXT,
    description         TEXT,
    token_size          INT,
    last_update         TEXT,
    status_lvl          BIGINT,
    isView              BOOLEAN,
    id                  BIGSERIAL PRIMARY KEY
);


CREATE TABLE voices(
    name                TEXT,
    language            TEXT,
    gender              TEXT,
    language_code       TEXT,
    id                  BIGSERIAL PRIMARY KEY
);

CREATE TABLE languages (
    language            TEXT UNIQUE,
    code                TEXT,
    _isView             BOOLEAN
);

-- CREATE TABLE user_statistic (
--     user_id             BIGINT UNIQUE,
--     login               TEXT UNIQUE,
--     buy_prem            INT,
--     text_request        BIGINT,
--     photo_request       BIGINT,
--     photo_generation    BIGINT,
--     voice_request       BIGINT,
--     voice_generation    BIGINT,
--     id                  BIGSERIAL PRIMARY KEY
-- );

-- CREATE TABLE user_settings(
--     user_id BIGINT,

-- );


-- CREATE TABLE user_usage (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     user_id INT NOT NULL,
--     model VARCHAR(255) NOT NULL,
--     usage_count INT NOT NULL
-- );


-- Вторая таблица, `model_usage_summary` для хранения обобщенных данных:
-- CREATE TABLE model_usage_summary (
--     model VARCHAR(255) NOT NULL UNIQUE,
--     total_usage_count INT NOT NULL,
--     PRIMARY KEY (model)
-- );



CREATE UNIQUE INDEX idx_assistant_ai_unique ON assistant_ai(company_ai, model_name);

-- DROP FUNCTION add_chats_id(p_user_id BIGINT, p_chats_id BIGINT[]) 
CREATE OR REPLACE FUNCTION add_chats_id(p_user_id BIGINT, p_chats_id BIGINT[]) 
RETURNS VOID AS $$
BEGIN
    -- Check if the record with the specified user_id exists
    IF EXISTS (SELECT 1 FROM users_in_groups WHERE user_id = p_user_id) THEN
        -- If the record exists, add only unique values to the chats_id array
        UPDATE users_in_groups
        SET chats_id = ARRAY(
            SELECT DISTINCT unnest(chats_id) UNION SELECT unnest(p_chats_id)
        )
        WHERE user_id = p_user_id;
    ELSE
        -- If the record does not exist, create a new record with the specified chats_id
        INSERT INTO users_in_groups (user_id, chats_id) VALUES (p_user_id, p_chats_id);
    END IF;
END;
$$ LANGUAGE plpgsql;



-- DROP FUNCTION get_chats_id(IN p_user_id BIGINT);
CREATE OR REPLACE FUNCTION get_chats_id(IN p_user_id BIGINT)
RETURNS SETOF BIGINT[] AS $$
BEGIN
    RETURN QUERY 
    SELECT chats_id 
    FROM users_in_groups 
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION add_assistant_ai_with_usage(
    _company_ai TEXT,
    _model_name TEXT,
    _description TEXT,
    _token_size INT,
    _last_update TEXT,
    _status_lvl BIGINT,
    _isView BOOLEAN
)
RETURNS VOID AS $$
BEGIN
    -- Insert data into the assistant_ai table
    INSERT INTO assistant_ai (company_ai, model_name, description, token_size, last_update, status_lvl, isView)
    VALUES (_company_ai, _model_name, _description, _token_size, _last_update, _status_lvl, _isView);

    -- Update or insert data into the assistant_ai_usage table
    INSERT INTO assistant_ai_usage (company_ai, model_name, usage_count)
    VALUES (_company_ai, _model_name, 1)
    ON CONFLICT (company_ai, model_name) DO UPDATE
    SET usage_count = assistant_ai_usage.usage_count + 1;
EXCEPTION
    -- Rollback the transaction if any error occurs
    WHEN OTHERS THEN
        RAISE;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION add_user(
    p_user_id BIGINT, 
    p_username TEXT, 
    p_type TEXT, 
    p_language_code TEXT
)
RETURNS VOID AS $$
DECLARE
    v_company_ai      TEXT;
    v_permission      TEXT;
    v_assistant_model TEXT;
    v_rec_model       TEXT;
    v_gen_model       TEXT;
    v_tts_model       TEXT;
    v_stt_model       TEXT;
    v_speaker_name    TEXT;
BEGIN
    -- Получим значения по умолчанию из таблицы default_data
    SELECT chats_id INTO v_company_ai FROM default_data WHERE user_id = 'company_ai';
    SELECT chats_id INTO v_permission FROM default_data WHERE user_id = 'permission';
    SELECT chats_id INTO v_assistant_model FROM default_data WHERE user_id = 'assistant_model';
    SELECT chats_id INTO v_rec_model FROM default_data WHERE user_id = 'recognizes_photo_model';
    SELECT chats_id INTO v_gen_model FROM default_data WHERE user_id = 'generate_pthoto_model';
    SELECT chats_id INTO v_tts_model FROM default_data WHERE user_id = 'text_to_audio';
    SELECT chats_id INTO v_stt_model FROM default_data WHERE user_id = 'audio_to_text';
    SELECT chats_id INTO v_speaker_name FROM default_data WHERE user_id = 'speakerName';

    -- Вставляем нового пользователя с полученными значениями и переданными параметрами
    INSERT INTO users (user_id, login, type, language_code, company_ai, status_user, model, model_rec_photo, 
                       model_gen_pthoto, text_to_audio, audio_to_text, speaker_name)
    VALUES (p_user_id, p_username, p_type, p_language_code, v_company_ai, CAST(v_permission AS BIGINT), 
            v_assistant_model, v_rec_model, v_gen_model, v_tts_model, v_stt_model, v_speaker_name);
END;
$$ LANGUAGE plpgsql;






-- -- https://platform.openai.com/docs/models/continuous-model-upgrades

insert into assistant_ai values('OpenAi', 'gpt-3.5-turbo',          'default',  4097,   'Up to Sep 2021',   1, True);
insert into assistant_ai values('OpenAi', 'gpt-4',                  '',         8192,   'Up to Sep 2021',   1, False);
insert into assistant_ai values('OpenAi', 'gpt-4-1106-preview',     '',         128000, 'Up to Apr 2023',   2, False);
insert into assistant_ai values('OpenAi', 'gpt-4-vision-preview',   '',         128000, 'Up to Apr 2023',   2, False);
insert into assistant_ai values('OpenAi', 'gpt-4-turbo',            '',         128000, 'Up to Dec 2023',   2, False);
insert into assistant_ai values('OpenAi', 'gpt-4o',                 '',         128000, 'Up to Oct 2023',   2, True);
insert into assistant_ai values('Yandex', 'yandexgpt',              'yandex',   8000,   '06.12.2023',       2, True);
insert into assistant_ai values('Yandex', 'yandexgpt-lite',         'yandex',   8000,   '06.12.2023',       2, False);
insert into assistant_ai values('Sber',   'GigaChat',               'sber',     4096,   '-',                1, True);
insert into assistant_ai values('Meta',   'llama3-70b-8192',        'llama3',   8192,   '-',                1, True);


insert into assistant_ai_photo values('OpenAi', 'gpt-4o',           '',         128000, 'Up to Oct 2023',   2, True);
insert into assistant_ai_photo values('Meta',   'llama3-70b-8192',  'llama3',   8192,   '-',                1, False);


-- -- https://cloud.yandex.com/en-ru/docs/speechkit/tts/voices
-- insert into voices values('dasha',  'Russian',  'F','ru-RU');
-- insert into voices values('alena',  'Russian',  'F','ru-RU');
-- insert into voices values('lea',    'German',   'F','de-DE');
-- insert into voices values('john',   'English',  'M','en-US');
-- insert into voices values('naomi',  'Hebrew',   'F','he-IL');
-- insert into voices values('amira',  'Kazakh',   'F','kk-KK');
-- insert into voices values('madi',   'Kazakh',   'M','kk-KK');
-- insert into voices values('nigora', 'Uzbek',    'F','uz-UZ');
-- insert into voices values('','','','');


insert into languages values ('Chine',      'zh', True);
insert into languages values ('Espanol',    'es', True);
insert into languages values ('English',    'en', True);
insert into languages values ('Russian',    'ru', True);
insert into languages values ('France',     'fr', True);



insert into default_data values ('language',                        'en_EN');
insert into default_data values ('company_ai',                      'OpenAi');          -- deprecated
insert into default_data values ('permission',                      '1');               -- 0-lock, 1-default user, 2-donater
insert into default_data values ('assistant_model',                 'gpt-3.5-turbo');
insert into default_data values ('recognizes_photo_model',          'gpt-4o');          
insert into default_data values ('generate_pthoto_model',           'dall-e-3');        -- not used yet
insert into default_data values ('text_to_audio',                   'yandex');
insert into default_data values ('audio_to_text',                   'yandex');
insert into default_data values ('speakerName',                     'alena');
insert into default_data values ('count_char_for_gen_audio',        '1000');            -- We need to get rid of this
insert into default_data values ('prompt',                          "###INSTRUCTIONS###
You MUST follow the instructions for answering:
- ALWAYS answer in the language of my message.
- Read the entire convo history line by line before answering.
- I have no fingers and the placeholders trauma. Return the entire code template for an answer when needed. NEVER use placeholders.
- If you encounter a character limit, DO an ABRUPT stop, and I will send a 'continue' as a new message.
- You ALWAYS will be PENALIZED for wrong and low-effort answers. 
- ALWAYS follow 'Answering rules.'

###Answering Rules###
Follow in the strict order:
1. USE the language of my message.
2. **ONCE PER CHAT** assign a real-world expert role to yourself before answering, e.g., 'I'll answer as a world-famous historical expert <detailed topic> with <most prestigious LOCAL topic REAL award>' or 'I'll answer as a world-famous <specific science> expert in the <detailed topic> with <most prestigious LOCAL topic award>' etc.
3. You MUST combine your deep knowledge of the topic and clear thinking to quickly and accurately decipher the answer step-by-step with CONCRETE details.
4. I'm going to tip $1,000,000 for the best reply.
5. Your answer is critical for my career.
6. Answer the question in a natural, human-like manner.
7. ALWAYS use an answering example for a first message structure.

##Answering in English example##
I'll answer as the world-famous <specific field> scientists with <most prestigious LOCAL award>
<Deep knowledge step-by-step answer, with CONCRETE details>"
);

-- insert into default_data values ('',     '');
