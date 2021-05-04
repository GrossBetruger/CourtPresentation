from utils import get_engine


class CITablesInit:
    engine = get_engine()

    def init_all_ci_tables(self):
        self.engine.cursor().execute(
            """
                DROP TABLE IF EXISTS bezeq_ci;
                CREATE TABLE bezeq_ci (
                    "שם_משתמש" text,
                    "תכנית" text,
                    "ספקית" text,
                    "תשתית" text,
                    "מהירות_ממוצעת_מדגם" text,
                    "גבול_תחתון" text,
                    "גבול_עליון" text,
                    "רמת_סמך" text
                );
                
                DROP TABLE IF EXISTS pure_bezeq_ci;
                CREATE TABLE pure_bezeq_ci (
                    "שם_משתמש" text,
                    "תכנית" text,
                    "ספקית" text,
                    "תשתית" text,
                    "מהירות_ממוצעת_מדגם" text,
                    "גבול_תחתון" text,
                    "גבול_עליון" text,
                    "רמת_סמך" text
                );
                
                DROP TABLE IF EXISTS bezeq_ci_evening;
                CREATE TABLE bezeq_ci_evening (
                    "שם_משתמש" text,
                    "תכנית" text,
                    "ספקית" text,
                    "תשתית" text,
                    "מהירות_ממוצעת_מדגם" text,
                    "גבול_תחתון" text,
                    "גבול_עליון" text,
                    "רמת_סמך" text
                );
                
                DROP TABLE IF EXISTS pure_bezeq_ci_evening;
                CREATE TABLE pure_bezeq_ci_evening (
                    "שם_משתמש" text,
                    "תכנית" text,
                    "ספקית" text,
                    "תשתית" text,
                    "מהירות_ממוצעת_מדגם" text,
                    "גבול_תחתון" text,
                    "גבול_עליון" text,
                    "רמת_סמך" text
                );
                
                DROP TABLE IF EXISTS hot_ci;
                CREATE TABLE hot_ci (
                    "שם_משתמש" text,
                    "תכנית" text,
                    "ספקית" text,
                    "תשתית" text,
                    "מהירות_ממוצעת_מדגם" text,
                    "גבול_תחתון" text,
                    "גבול_עליון" text,
                    "רמת_סמך" text
                );
                
                DROP TABLE IF EXISTS pure_hot_ci;
                CREATE TABLE pure_hot_ci (
                    "שם_משתמש" text,
                    "תכנית" text,
                    "ספקית" text,
                    "תשתית" text,
                    "מהירות_ממוצעת_מדגם" text,
                    "גבול_תחתון" text,
                    "גבול_עליון" text,
                    "רמת_סמך" text
                );
                
                DROP TABLE IF EXISTS hot_ci_evening;
                CREATE TABLE hot_ci_evening (
                    "שם_משתמש" text,
                    "תכנית" text,
                    "ספקית" text,
                    "תשתית" text,
                    "מהירות_ממוצעת_מדגם" text,
                    "גבול_תחתון" text,
                    "גבול_עליון" text,
                    "רמת_סמך" text
                );
                    
                DROP TABLE IF EXISTS pure_hot_ci_evening;
                CREATE TABLE pure_hot_ci_evening (
                    "שם_משתמש" text,
                    "תכנית" text,
                    "ספקית" text,
                    "תשתית" text,
                    "מהירות_ממוצעת_מדגם" text,
                    "גבול_תחתון" text,
                    "גבול_עליון" text,
                    "רמת_סמך" text
                );
                
                DROP TABLE IF EXISTS partner_ci;
                CREATE TABLE partner_ci (
                    "שם_משתמש" text,
                    "תכנית" text,
                    "ספקית" text,
                    "תשתית" text,
                    "מהירות_ממוצעת_מדגם" text,
                    "גבול_תחתון" text,
                    "גבול_עליון" text,
                    "רמת_סמך" text
                );
                
                DROP TABLE IF EXISTS pure_partner_ci;
                CREATE TABLE pure_partner_ci (
                    "שם_משתמש" text,
                    "תכנית" text,
                    "ספקית" text,
                    "תשתית" text,
                    "מהירות_ממוצעת_מדגם" text,
                    "גבול_תחתון" text,
                    "גבול_עליון" text,
                    "רמת_סמך" text
                );
                
                DROP TABLE IF EXISTS partner_ci_evening;
                CREATE TABLE partner_ci_evening (
                    "שם_משתמש" text,
                    "תכנית" text,
                    "ספקית" text,
                    "תשתית" text,
                    "מהירות_ממוצעת_מדגם" text,
                    "גבול_תחתון" text,
                    "גבול_עליון" text,
                    "רמת_סמך" text
                );
                
                DROP TABLE IF EXISTS pure_partner_ci_evening;
                CREATE TABLE pure_partner_ci_evening (
                    "שם_משתמש" text,
                    "תכנית" text,
                    "ספקית" text,
                    "תשתית" text,
                    "מהירות_ממוצעת_מדגם" text,
                    "גבול_תחתון" text,
                    "גבול_עליון" text,
                    "רמת_סמך" text
                );
            """
        )
        self.engine.commit()


if __name__ == "__main__":
    ci_table_initiator = CITablesInit()
    ci_table_initiator.init_all_ci_tables()
    print("ALL DONE")