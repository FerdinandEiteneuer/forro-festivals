from forro_festivals.routes import auth, admin, info, add_festival, update_festival

blueprints = [auth.bp, admin.bp, info.bp, add_festival.bp, update_festival.bp]
