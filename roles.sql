--Vue Wishliste pour les utilisateurs
CREATE VIEW library.WishListe_view AS
SELECT * FROM library.WishListe
WHERE user_id = current_user;

--Fonction wishliste insert
CREATE OR REPLACE FUNCTION check_wishlist_insert()
RETURNS TRIGGER AS $$
BEGIN
    IF current_user = 'moderateur' THEN
        RAISE EXCEPTION 'Les modérateurs ne peuvent pas ajouter des entrées.';
    ELSIF NEW.user_id <> current_user THEN
        RAISE EXCEPTION 'Vous ne pouvez ajouter que pour votre propre compte.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

--Trigger wishliste insert
CREATE TRIGGER trigger_wishlist_insert
BEFORE INSERT ON library.WishListe
FOR EACH ROW EXECUTE FUNCTION check_wishlist_insert();


-- Fonction wishliste delete
CREATE OR REPLACE FUNCTION check_wishlist_delete()
RETURNS TRIGGER AS $$
BEGIN
    -- Si un utilisateur normal tente de supprimer autre chose que ses propres entrées
    IF current_user = 'utilisateur' AND OLD.user_id <> current_user THEN
        RAISE EXCEPTION 'Vous ne pouvez supprimer que vos propres entrées.';

    -- Si un modérateur tente de supprimer une entrée d'un autre modérateur, ou des devs
    ELSIF current_user = 'moderateur' AND OLD.user_id IN ('moderateur', 'dev_tlss', 'dev_bigboss') THEN
        RAISE EXCEPTION 'Vous ne pouvez pas supprimer les entrées des modérateurs et des administrateurs.';
    END IF;

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;



--Trigger wishliste delete
CREATE TRIGGER trigger_wishlist_delete
BEFORE DELETE ON library.WishListe
FOR EACH ROW EXECUTE FUNCTION check_wishlist_delete();





-- Vue user
CREATE OR REPLACE VIEW library._Users_view AS
SELECT * 
FROM library._Users
WHERE user_id = current_user;



-- Fonction user insert
CREATE OR REPLACE FUNCTION library.check_insert_user()
RETURNS TRIGGER AS $$
BEGIN
  -- Vérifie si le user_id de l'utilisateur correspond à l'identifiant de l'utilisateur connecté
  IF NEW.user_id != current_user THEN
    RAISE EXCEPTION 'Vous ne pouvez insérer que vos propres données.';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger user insert
CREATE TRIGGER trigger_insert_user
BEFORE INSERT ON library._Users
FOR EACH ROW EXECUTE FUNCTION library.check_insert_user();



-- Fonction user update
CREATE OR REPLACE FUNCTION library.check_update_user()
RETURNS TRIGGER AS $$
BEGIN
  -- Vérifie si l'utilisateur tente de mettre à jour uniquement ses propres données
  IF NEW.user_id != current_user THEN
    RAISE EXCEPTION 'Vous ne pouvez mettre à jour que vos propres données.';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- Trigger user update
CREATE TRIGGER trigger_update_user
BEFORE UPDATE ON library._Users
FOR EACH ROW EXECUTE FUNCTION library.check_update_user();

-- Fonction user delete
CREATE OR REPLACE FUNCTION library.check_delete_user()
RETURNS TRIGGER AS $$
BEGIN
  -- Vérifie si l'utilisateur tente de supprimer uniquement ses propres données
  IF OLD.user_id != current_user THEN
    RAISE EXCEPTION 'Vous ne pouvez supprimer que vos propres données.';
  END IF;
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Trigger user delete
CREATE TRIGGER trigger_delete_user
BEFORE DELETE ON library._Users
FOR EACH ROW
EXECUTE FUNCTION library.check_delete_user();





-- Rôle superadmin (privilèges totaux, à utiliser avec prudence)
CREATE ROLE superadmin WITH LOGIN PASSWORD 'mdp_secure' SUPERUSER CREATEDB CREATEROLE;

-- Rôle dev TLSS
CREATE ROLE dev_tlss WITH LOGIN PASSWORD 'mdp_secure' CREATEDB;
GRANT CONNECT ON DATABASE sae TO dev_tlss;
GRANT USAGE, CREATE ON SCHEMA library TO dev_tlss;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA library TO dev_tlss;
REVOKE SELECT (passwords) ON library._Users FROM dev_tlss;

-- Rôle dev Bigboss
CREATE ROLE dev_bigboss WITH LOGIN PASSWORD 'mdp_secure';
GRANT CONNECT ON DATABASE sae TO dev_bigboss;
GRANT USAGE ON SCHEMA library TO dev_bigboss;
GRANT SELECT ON ALL TABLES IN SCHEMA library TO dev_bigboss;
REVOKE SELECT (passwords) ON library._Users FROM dev_bigboss;

-- Rôle moderateur
CREATE ROLE moderateur WITH LOGIN PASSWORD 'mdp_secure';

GRANT CONNECT ON DATABASE sae TO moderateur;
GRANT USAGE ON SCHEMA library TO moderateur;
GRANT SELECT, UPDATE, DELETE ON library.Book TO moderateur;
GRANT SELECT, UPDATE, DELETE ON library._Users TO moderateur;
GRANT SELECT ON library.WishListe TO moderateur;
GRANT DELETE ON library.WishListe TO moderateur;
REVOKE INSERT, UPDATE ON library.WishListe FROM moderateur;
REVOKE SELECT (passwords) ON library._Users FROM moderateur;


-- Rôle analyste, qui a seulement accès en lecture
CREATE ROLE analyste WITH LOGIN PASSWORD 'mdp_secure';

GRANT CONNECT ON DATABASE sae TO analyste;
GRANT USAGE ON SCHEMA library TO analyste;
GRANT SELECT ON ALL TABLES IN SCHEMA library TO analyste;
REVOKE SELECT (name, passwords) ON library._Users FROM analyste;

-- Rôle utilisateur, qui a des permissions limitées
CREATE ROLE utilisateur WITH LOGIN PASSWORD 'mdp_secure';
GRANT CONNECT ON DATABASE sae TO utilisateur;
GRANT USAGE ON SCHEMA library TO utilisateur;
GRANT SELECT ON library.book_view TO utilisateur;
GRANT SELECT ON library.author_view TO utilisateur;
GRANT SELECT ON library.Author TO utilisateur;
GRANT SELECT ON library.Wrote TO utilisateur;
GRANT SELECT ON library.top_books TO utilisateur;
GRANT SELECT ON library.Book TO utilisateur;
GRANT SELECT ON library.Genre_and_vote TO utilisateur;
GRANT SELECT ON library.Genre TO utilisateur;
GRANT SELECT ON library.Serie TO utilisateur;
GRANT SELECT ON library.Serie_of_book TO utilisateur;

REVOKE SELECT ON library.WishListe FROM utilisateur;
GRANT SELECT ON library.WishListe_view TO utilisateur;

GRANT SELECT, INSERT, DELETE ON library.WishListe TO utilisateur;


GRANT INSERT, UPDATE, DELETE ON library._Users TO utilisateur;
GRANT SELECT ON library._Users_view TO utilisateur;