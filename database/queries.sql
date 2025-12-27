MATCH (target:User {user_id: "AF7XNTURXVPO55T5EP4B4DVPQPPQ"})-[r1:RATED]->(p:Product)<-[r2:RATED]-(other:User)
WHERE other <> target

// tworzymy podreczny zestaw danych z liczba wspolnych produktow i ocenami
WITH target, other, 
    count(p) AS commonProducts, 
    collect({
    product: p.parent_asin, 
    targetRating: r1.rating, 
    otherRating: r2.rating
    }) AS ratings
WHERE commonProducts >= 2
// bierzemy pod uwage tylko tych uzytkownikow, ktorzy ocenili co najmniej 2 wspolne produkty

RETURN other.user_id, commonProducts, ratings